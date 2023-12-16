CREATE OR REPLACE FUNCTION null_parentpk_trigger() RETURNS TRIGGER AS
$$
DECLARE
	parent_asset notes.assets%ROWTYPE;
BEGIN
	IF NEW.parentpk IS NULL THEN
		NEW.parentpk := NEW.pk;
		RAISE DEBUG 'insert parent asset: NEW.parentpk := %', NEW.pk;
	ELSEIF NEW.title IS NOT NULL THEN
		RAISE EXCEPTION 'child asset NEW.title must be null';
	ELSE
		SELECT * INTO parent_asset FROM notes.assets WHERE (pk = NEW.parentpk);
		IF parent_asset IS NOT NULL THEN
			NEW.title := parent_asset.title;	
			RAISE DEBUG 'insert child asset: NEW.title := %', parent_asset.title;
		ELSE
			RAISE EXCEPTION 'parent_asset where pk = % does not exist', NEW.pk;
		END IF;
	END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER null_parentpk BEFORE INSERT ON notes.assets
	FOR EACH ROW EXECUTE FUNCTION null_parentpk_trigger();
