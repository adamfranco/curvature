--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.5
-- Dumped by pg_dump version 9.5.5

-- Started on 2016-12-14 02:39:56 EST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 10 (class 2615 OID 19339)
-- Name: topology; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA topology;


ALTER SCHEMA topology OWNER TO postgres;

--
-- TOC entry 1 (class 3079 OID 12623)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 3895 (class 0 OID 0)
-- Dependencies: 1
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- TOC entry 2 (class 3079 OID 17866)
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- TOC entry 3896 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry, geography, and raster spatial types and functions';


--
-- TOC entry 3 (class 3079 OID 19340)
-- Name: postgis_topology; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS postgis_topology WITH SCHEMA topology;


--
-- TOC entry 3897 (class 0 OID 0)
-- Dependencies: 3
-- Name: EXTENSION postgis_topology; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_topology IS 'PostGIS topology spatial types and functions';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 205 (class 1259 OID 19489)
-- Name: curvature_segments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE curvature_segments (
    id character(40) NOT NULL,
    name character varying(100),
    curvature integer,
    geom geometry(LineString),
    paved boolean DEFAULT false NOT NULL,
    fk_source integer,
    length integer,
    surface character varying(50),
    highway character varying(50)
);


ALTER TABLE curvature_segments OWNER TO postgres;

--
-- TOC entry 3898 (class 0 OID 0)
-- Dependencies: 205
-- Name: COLUMN curvature_segments.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN curvature_segments.id IS 'Sha1 hash of the constituent way-ids.';


--
-- TOC entry 208 (class 1259 OID 112666)
-- Name: segment_ways; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE segment_ways (
    fk_segment character(40) NOT NULL,
    id integer NOT NULL,
    name character varying(100),
    highway character varying(20),
    surface character varying(20),
    curvature integer,
    length integer,
    min_lon double precision,
    max_lon double precision,
    min_lat double precision,
    max_lat double precision,
    "position" integer
);


ALTER TABLE segment_ways OWNER TO postgres;

--
-- TOC entry 3900 (class 0 OID 0)
-- Dependencies: 208
-- Name: COLUMN segment_ways.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN segment_ways.id IS 'The OSM Id of the way.';


--
-- TOC entry 3901 (class 0 OID 0)
-- Dependencies: 208
-- Name: COLUMN segment_ways.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN segment_ways.name IS 'The name of the way.';


--
-- TOC entry 3902 (class 0 OID 0)
-- Dependencies: 208
-- Name: COLUMN segment_ways.highway; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN segment_ways.highway IS 'The OSM highway tag’s value.';


--
-- TOC entry 3903 (class 0 OID 0)
-- Dependencies: 208
-- Name: COLUMN segment_ways.surface; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN segment_ways.surface IS 'The OSM ‘surface’ tag value.';


--
-- TOC entry 207 (class 1259 OID 28646)
-- Name: sources; Type: TABLE; Schema: public; Owner: curvature_app
--

CREATE TABLE sources (
    id integer NOT NULL,
    source character varying(100)
);


ALTER TABLE sources OWNER TO curvature_app;

--
-- TOC entry 206 (class 1259 OID 28644)
-- Name: sources_id_seq; Type: SEQUENCE; Schema: public; Owner: curvature_app
--

CREATE SEQUENCE sources_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE sources_id_seq OWNER TO curvature_app;

--
-- TOC entry 3905 (class 0 OID 0)
-- Dependencies: 206
-- Name: sources_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: curvature_app
--

ALTER SEQUENCE sources_id_seq OWNED BY sources.id;


--
-- TOC entry 3753 (class 2604 OID 28649)
-- Name: id; Type: DEFAULT; Schema: public; Owner: curvature_app
--

ALTER TABLE ONLY sources ALTER COLUMN id SET DEFAULT nextval('sources_id_seq'::regclass);


--
-- TOC entry 3757 (class 2606 OID 104481)
-- Name: curvature_segments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY curvature_segments
    ADD CONSTRAINT curvature_segments_pkey PRIMARY KEY (id);


--
-- TOC entry 3764 (class 2606 OID 112670)
-- Name: segment_ways_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY segment_ways
    ADD CONSTRAINT segment_ways_pkey PRIMARY KEY (fk_segment, id);


--
-- TOC entry 3761 (class 2606 OID 28651)
-- Name: sources_pkey; Type: CONSTRAINT; Schema: public; Owner: curvature_app
--

ALTER TABLE ONLY sources
    ADD CONSTRAINT sources_pkey PRIMARY KEY (id);


--
-- TOC entry 3754 (class 1259 OID 19514)
-- Name: curvature_segment_geom; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX curvature_segment_geom ON curvature_segments USING gist (geom);


--
-- TOC entry 3755 (class 1259 OID 120967)
-- Name: curvature_segments_length_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX curvature_segments_length_idx ON curvature_segments USING btree (curvature, length);


--
-- TOC entry 3758 (class 1259 OID 28657)
-- Name: fki_foreign_key_source; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_foreign_key_source ON curvature_segments USING btree (fk_source);


--
-- TOC entry 3759 (class 1259 OID 56200)
-- Name: length_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX length_idx ON curvature_segments USING btree (length);


--
-- TOC entry 3762 (class 1259 OID 120966)
-- Name: segment_ways_fk_segment_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX segment_ways_fk_segment_idx ON segment_ways USING btree (fk_segment);


--
-- TOC entry 3766 (class 2606 OID 112671)
-- Name: fk_segment; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY segment_ways
    ADD CONSTRAINT fk_segment FOREIGN KEY (fk_segment) REFERENCES curvature_segments(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3765 (class 2606 OID 28652)
-- Name: foreign_key_source; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY curvature_segments
    ADD CONSTRAINT foreign_key_source FOREIGN KEY (fk_source) REFERENCES sources(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3894 (class 0 OID 0)
-- Dependencies: 8
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- TOC entry 3899 (class 0 OID 0)
-- Dependencies: 205
-- Name: curvature_segments; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE curvature_segments FROM PUBLIC;
REVOKE ALL ON TABLE curvature_segments FROM postgres;
GRANT ALL ON TABLE curvature_segments TO postgres;
GRANT ALL ON TABLE curvature_segments TO curvature_app;


--
-- TOC entry 3904 (class 0 OID 0)
-- Dependencies: 208
-- Name: segment_ways; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE segment_ways FROM PUBLIC;
REVOKE ALL ON TABLE segment_ways FROM postgres;
GRANT ALL ON TABLE segment_ways TO postgres;
GRANT ALL ON TABLE segment_ways TO curvature_app;


-- Completed on 2016-12-14 02:39:56 EST

--
-- PostgreSQL database dump complete
--

