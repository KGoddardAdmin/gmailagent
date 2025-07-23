# Google Cloud Audit Log Filter for Gmail OAuth

## Log Filter Query

```
LOG_ID("cloudaudit.googleapis.com/activity") OR 
LOG_ID("externalaudit.googleapis.com/activity") OR 
LOG_ID("cloudaudit.googleapis.com/system_event") OR 
LOG_ID("externalaudit.googleapis.com/system_event") OR 
LOG_ID("cloudaudit.googleapis.com/access_transparency") OR 
LOG_ID("externalaudit.googleapis.com/access_transparency")
```

## Purpose

This filter captures all audit logs related to:
- **Activity Logs**: User and service account activities
- **System Event Logs**: System-level events and changes
- **Access Transparency Logs**: Google personnel access to your data

## Usage

1. Go to [Google Cloud Console Logs Explorer](https://console.cloud.google.com/logs/query)
2. Paste the filter in the query builder
3. Set your time range
4. Click "Run Query"

## Log Types Explained

### Activity Logs (`cloudaudit.googleapis.com/activity`)
- OAuth authorization events
- API calls made by your Gmail MCP server
- Permission grants and revocations
- Token refresh events

### System Event Logs (`cloudaudit.googleapis.com/system_event`)
- Service configuration changes
- System maintenance events
- Automatic security updates

### Access Transparency Logs (`cloudaudit.googleapis.com/access_transparency`)
- Records when Google support or engineering accesses your data
- Provides reason and justification for access
- Helps ensure data privacy compliance

## Monitoring OAuth Events

To specifically monitor Gmail OAuth events, you can enhance the filter:

```
(LOG_ID("cloudaudit.googleapis.com/activity") OR 
LOG_ID("externalaudit.googleapis.com/activity")) AND
resource.type="audited_resource" AND
protoPayload.serviceName="gmail.googleapis.com"
```

## Common OAuth Events to Monitor

1. **Authorization Grant**
   - `protoPayload.methodName="google.auth.oauth2.authorize"`
   
2. **Token Exchange**
   - `protoPayload.methodName="google.auth.oauth2.token"`
   
3. **Token Refresh**
   - `protoPayload.methodName="google.auth.oauth2.refresh"`
   
4. **Scope Changes**
   - Look for changes in `protoPayload.request.scope`

## Security Best Practices

1. **Set up alerts** for unusual authorization patterns
2. **Monitor failed authentication** attempts
3. **Track scope escalations** (especially for delete permissions)
4. **Review access from unknown IPs** or locations
5. **Audit token refresh patterns** for anomalies

## Example Alert Query

To alert on new OAuth authorizations:

```
LOG_ID("cloudaudit.googleapis.com/activity") AND
protoPayload.methodName="google.auth.oauth2.authorize" AND
protoPayload.serviceName="gmail.googleapis.com" AND
severity="INFO"
```

## Related Documentation

- [Google Cloud Audit Logs](https://cloud.google.com/logging/docs/audit)
- [Gmail API Audit Logging](https://developers.google.com/gmail/api/guides/logging)
- [OAuth 2.0 Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)