-- Para ver o Phantom Read a dar
BEGIN TRANSACTION
	SELECT * FROM MEI_TRAB.dbo.LogOperations
	WHERE EventType = 'O'

	-- Delay para vermos as altera��es
	WAITFOR DELAY '00:00:30'

	SELECT * FROM MEI_TRAB.dbo.LogOperations
	WHERE EventType = 'O'
COMMIT TRANSACTION

