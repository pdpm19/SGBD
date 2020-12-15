-- Para ver o Dirty Read a dar
-- SET TRANSACTION ISOLATION LEVEL READ COMMITTED
BEGIN TRANSACTION; 
	DECLARE @cont INT = 1;
	WHILE @cont <= 30
	BEGIN
		UPDATE MEI_TRAB.dbo.Encomenda
		SET Morada = (SELECT CAST(@cont AS VARCHAR(max)))
		WHERE EncID = '2'
		-- Para ver a mudan�a em a��o
		/*
		BEGIN TRANSACTION;
		
		SELECT * FROM MEI_TRAB.dbo.Encomenda
		WHERE EncID = 2
		COMMIT TRANSACTION;
		*/
		-- Timer para vermos que a mudan�a ficou em espera (de ser validada)
		-- wait for 1 Sec
		WAITFOR DELAY '00:00:01'
		SET @cont = @cont + 1;
	END;
-- Fazemos agora Rollback
ROLLBACK TRANSACTION;

-- Para ver que est� tudo bem
BEGIN TRANSACTION;
SELECT * FROM MEI_TRAB.dbo.Encomenda
WHERE EncID = 2
COMMIT TRANSACTION;

