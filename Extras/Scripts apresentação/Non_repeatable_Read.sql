-- Para ver o Non Repeatable Read a dar
-- SET TRANSACTION ISOLATION LEVEL READ COMMITTED
BEGIN TRANSACTION
	SELECT * FROM MEI_TRAB.dbo.Encomenda
	WHERE EncID = '2'

	SELECT * FROM MEI_TRAB.dbo.Encomenda
	WHERE EncID = '2'

	-- Delay para vermos as alterações
	WAITFOR DELAY '00:00:30'

	SELECT * FROM MEI_TRAB.dbo.Encomenda
	WHERE EncID = '2'
COMMIT TRANSACTION