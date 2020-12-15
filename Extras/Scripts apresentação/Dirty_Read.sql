-- Para ver o Dirty Read a dar
-- SET TRANSACTION ISOLATION LEVEL READ COMMITTED
BEGIN TRANSACTION; 
	DECLARE @cont INT = 1;
	WHILE @cont <= 30
	BEGIN
		UPDATE MEI_TRAB.dbo.Encomenda
		SET Morada = (SELECT CAST(@cont AS VARCHAR(max)))
		WHERE EncID = '2'
		-- Para ver a mudança em ação
		/*
		BEGIN TRANSACTION;
		
		SELECT * FROM MEI_TRAB.dbo.Encomenda
		WHERE EncID = 2
		COMMIT TRANSACTION;
		*/
		-- Timer para vermos que a mudança ficou em espera (de ser validada)
		-- wait for 1 Sec
		WAITFOR DELAY '00:00:01'
		SET @cont = @cont + 1;
	END;
-- Fazemos agora Rollback
ROLLBACK TRANSACTION;

-- Para ver que está tudo bem
BEGIN TRANSACTION;
SELECT * FROM MEI_TRAB.dbo.Encomenda
WHERE EncID = 2
COMMIT TRANSACTION;

