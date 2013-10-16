-- schema updates for namespaces

BEGIN;


CREATE TABLE namespace (
        id SERIAL NOT NULL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
) WITHOUT OIDS;

INSERT INTO namespace (id, name) VALUES (0, 'DEFAULT');



ALTER TABLE build ADD COLUMN namespace_id INTEGER DEFAULT 0;
-- can be null


ALTER TABLE build DROP CONSTRAINT build_pkg_ver_rel;
ALTER TABLE build ADD CONSTRAINT build_namespace_sanity UNIQUE (namespace_id, pkg_id, version, release);
--      note that namespace_id can be null, which allows arbitrary nvr overlap


ALTER TABLE rpminfo ADD COLUMN namespace_id INTEGER DEFAULT 0;
-- can be null


ALTER TABLE rpminfo DROP CONSTRAINT rpminfo_unique_nvra;
ALTER TABLE rpminfo ADD CONSTRAINT rpminfo_namespace_sanity UNIQUE (namespace_id,name,version,release,arch,external_repo_id);
--      note that namespace_id can be null, which allows arbitrary nvr overlap
ALTER TABLE rpminfo ADD CONSTRAINT external_no_namespace CHECK (external_repo_id = 0 OR namespace_id=0);
ALTER TABLE rpminfo ADD CONSTRAINT external_no_build CHECK (external_repo_id = 0 OR build_id IS NULL);

-- now we need to set all the builds and rpms to default namespace
UPDATE build set namespace_id=0;

UPDATE rpminfo set namespace_id=0;


-- namespaces for tags
CREATE TABLE tag_extra_config (
        tag_id INTEGER NOT NULL REFERENCES tag(id),
        namespace_id INTEGER REFERENCES namespace(id) DEFAULT 0,
-- versioned - see desc above
        create_event INTEGER NOT NULL REFERENCES events(id) DEFAULT get_event(),
        revoke_event INTEGER REFERENCES events(id),
        creator_id INTEGER NOT NULL REFERENCES users(id),
        revoker_id INTEGER REFERENCES users(id),
        active BOOLEAN DEFAULT 'true' CHECK (active),
        CONSTRAINT active_revoke_sane CHECK (
                (active IS NULL AND revoke_event IS NOT NULL AND revoker_id IS NOT NULL)
                OR (active IS NOT NULL AND revoke_event IS NULL AND revoker_id IS NULL)),
        PRIMARY KEY (create_event, tag_id),
        UNIQUE (tag_id,active)
) WITHOUT OIDS;


COMMIT;

