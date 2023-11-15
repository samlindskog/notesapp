CREATE OR REPLACE FUNCTION null_parentid_trigger() RETURNS TRIGGER AS
$$
DECLARE
	parent_asset notes.assets%ROWTYPE;
BEGIN
	IF NEW.parentid IS NULL THEN
		NEW.parentid := NEW.id;
		RAISE DEBUG 'insert parent asset: NEW.parentid := %', NEW.id;
	ELSEIF NEW.title IS NOT NULL THEN
		RAISE EXCEPTION 'child asset NEW.title must be null';
	ELSE
		SELECT * INTO parent_asset FROM notes.assets WHERE (id = NEW.parentid);
		IF parent_asset IS NOT NULL THEN
			NEW.title := parent_asset.title;	
			RAISE DEBUG 'insert child asset: NEW.title := %', parent_asset.title;
		ELSE
			RAISE EXCEPTION 'parent_asset where id = % does not exist', NEW.parentid;
		END IF;
	END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER null_parentid BEFORE INSERT ON notes.assets
	FOR EACH ROW EXECUTE FUNCTION null_parentid_trigger();
