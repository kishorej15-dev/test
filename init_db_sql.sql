-- Run once on your SQL Server to create the token table:
CREATE TABLE zoho_tokens (
    service VARCHAR(100) PRIMARY KEY,
    access_token VARCHAR(MAX),
    refresh_token VARCHAR(MAX),
    expires_at DATETIMEOFFSET NULL,
    updated_at DATETIMEOFFSET DEFAULT SYSUTCDATETIME()
);

-- Example insert (replace values if needed):
INSERT INTO zoho_tokens(service, access_token, refresh_token, expires_at)
VALUES('zoho_bigin',
       '1000.addac49da6a97d98e9fd4deb02d9b99e.430658aa62b2b0aefd17b7d84ae41bd0',
       '1000.7be79d01ac54e88968827f579ec67881.b6af36cbff584305820f52b5772f311b',
       NULL);
