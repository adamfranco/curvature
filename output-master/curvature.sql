--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.4
-- Dumped by pg_dump version 9.5.5

-- Started on 2016-12-17 18:05:22 EST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;


--
--



SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 207 (class 1259 OID 19816)
-- Name: curvature_segments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE curvature_segments (
    id character(40) NOT NULL,
    name character varying(100),
    curvature integer,
    length integer,
    surface character varying(50),
    highway character varying(100),
    paved boolean DEFAULT false NOT NULL,
    fk_source integer,
    geom geometry(LineString)
);


--
-- TOC entry 4484 (class 0 OID 0)
-- Dependencies: 207
-- Name: COLUMN curvature_segments.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN curvature_segments.id IS 'Sha1 hash of the constituent way-ids.';


--
-- TOC entry 208 (class 1259 OID 19823)
-- Name: segment_ways; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE segment_ways (
    fk_segment character(40) NOT NULL,
    "position" integer,
    id integer NOT NULL,
    name character varying(100),
    highway character varying(20),
    surface character varying(20),
    curvature integer,
    length integer,
    min_lon double precision,
    max_lon double precision,
    min_lat double precision,
    max_lat double precision
);


--
-- TOC entry 4485 (class 0 OID 0)
-- Dependencies: 208
-- Name: COLUMN segment_ways.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN segment_ways.id IS 'The OSM Id of the way.';


--
-- TOC entry 4486 (class 0 OID 0)
-- Dependencies: 208
-- Name: COLUMN segment_ways.name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN segment_ways.name IS 'The name of the way.';


--
-- TOC entry 4487 (class 0 OID 0)
-- Dependencies: 208
-- Name: COLUMN segment_ways.highway; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN segment_ways.highway IS 'The OSM highway tag’s value.';


--
-- TOC entry 4488 (class 0 OID 0)
-- Dependencies: 208
-- Name: COLUMN segment_ways.surface; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN segment_ways.surface IS 'The OSM ‘surface’ tag value.';


--
-- TOC entry 209 (class 1259 OID 19826)
-- Name: sources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE sources (
    id integer NOT NULL,
    source character varying(100)
);


--
-- TOC entry 210 (class 1259 OID 19829)
-- Name: sources_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE sources_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4489 (class 0 OID 0)
-- Dependencies: 210
-- Name: sources_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE sources_id_seq OWNED BY sources.id;


--
-- TOC entry 4344 (class 2604 OID 19831)
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY sources ALTER COLUMN id SET DEFAULT nextval('sources_id_seq'::regclass);


--
-- TOC entry 4348 (class 2606 OID 19833)
-- Name: curvature_segments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY curvature_segments
    ADD CONSTRAINT curvature_segments_pkey PRIMARY KEY (id);


--
-- TOC entry 4353 (class 2606 OID 19835)
-- Name: segment_ways_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY segment_ways
    ADD CONSTRAINT segment_ways_pkey PRIMARY KEY (fk_segment, id);


--
-- TOC entry 4355 (class 2606 OID 19837)
-- Name: sources_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY sources
    ADD CONSTRAINT sources_pkey PRIMARY KEY (id);


--
-- TOC entry 4345 (class 1259 OID 19838)
-- Name: curvature_segment_geom; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX curvature_segment_geom ON curvature_segments USING gist (geom);


--
-- TOC entry 4346 (class 1259 OID 19839)
-- Name: curvature_segments_length_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX curvature_segments_length_idx ON curvature_segments USING btree (curvature, length);


--
-- TOC entry 4349 (class 1259 OID 19840)
-- Name: fki_foreign_key_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_foreign_key_source ON curvature_segments USING btree (fk_source);


--
-- TOC entry 4350 (class 1259 OID 19841)
-- Name: length_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX length_idx ON curvature_segments USING btree (length);


--
-- TOC entry 4351 (class 1259 OID 19842)
-- Name: segment_ways_fk_segment_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX segment_ways_fk_segment_idx ON segment_ways USING btree (fk_segment);


--
-- TOC entry 4357 (class 2606 OID 19843)
-- Name: fk_segment; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY segment_ways
    ADD CONSTRAINT fk_segment FOREIGN KEY (fk_segment) REFERENCES curvature_segments(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 4356 (class 2606 OID 19848)
-- Name: foreign_key_source; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY curvature_segments
    ADD CONSTRAINT foreign_key_source FOREIGN KEY (fk_source) REFERENCES sources(id) ON UPDATE CASCADE ON DELETE CASCADE;


-- Completed on 2016-12-17 18:05:36 EST

--
-- PostgreSQL database dump complete
--

