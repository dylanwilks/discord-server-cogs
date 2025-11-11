MERGE UserServerPerms AS Target
USING 
    (
    SELECT  ? as UserID,
	    ? as ServerName,
	    ? as Permission
    ) AS Source
ON  (Target.UserID = Source.UserID) AND 
    (Target.ServerName = Source.ServerName)

WHEN MATCHED THEN
    UPDATE SET Target.Permission = Source.Permission

WHEN NOT MATCHED BY Target THEN
    INSERT VALUES (Source.UserID, Source.ServerName, Source.Permission)
