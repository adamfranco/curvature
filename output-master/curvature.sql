--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.4
-- Dumped by pg_dump version 9.5.5

-- Started on 2017-01-04 22:33:06 EST

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
    id integer NOT NULL,
    id_hash character(40) NOT NULL,
    name character varying(100),
    curvature integer,
    length integer,
    fk_surface integer NOT NULL,
    fk_highway integer NOT NULL,
    paved boolean DEFAULT false NOT NULL,
    fk_source integer,
    geom geometry(LineString),
    hash character(40)
);


--
-- TOC entry 4507 (class 0 OID 0)
-- Dependencies: 207
-- Name: COLUMN curvature_segments.id_hash; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN curvature_segments.id_hash IS 'Sha1 hash of the constituent way-ids.';


--
-- TOC entry 4508 (class 0 OID 0)
-- Dependencies: 207
-- Name: COLUMN curvature_segments.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN curvature_segments.id IS 'Synthetic auto-increment id for joining.';


--
-- TOC entry 213 (class 1259 OID 38313)
-- Name: curvature_segments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE curvature_segments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4509 (class 0 OID 0)
-- Dependencies: 213
-- Name: curvature_segments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE curvature_segments_id_seq OWNED BY curvature_segments.id;


--
-- TOC entry 208 (class 1259 OID 19823)
-- Name: segment_ways; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE segment_ways (
    fk_segment integer NOT NULL,
    "position" integer,
    id integer NOT NULL,
    name character varying(100),
    fk_highway integer NOT NULL,
    fk_surface integer NOT NULL,
    curvature integer,
    length integer,
    min_lon double precision,
    max_lon double precision,
    min_lat double precision,
    max_lat double precision
);


--
-- TOC entry 4510 (class 0 OID 0)
-- Dependencies: 208
-- Name: COLUMN segment_ways.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN segment_ways.id IS 'The OSM Id of the way.';


--
-- TOC entry 4511 (class 0 OID 0)
-- Dependencies: 208
-- Name: COLUMN segment_ways.name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN segment_ways.name IS 'The name of the way.';


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
-- TOC entry 4512 (class 0 OID 0)
-- Dependencies: 210
-- Name: sources_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE sources_id_seq OWNED BY sources.id;


--
-- TOC entry 212 (class 1259 OID 38114)
-- Name: tags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE tags (
    tag_id integer NOT NULL,
    tag_name character varying(100),
    tag_value character varying(100)
);


--
-- TOC entry 211 (class 1259 OID 38112)
-- Name: tags_tag_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE tags_tag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4513 (class 0 OID 0)
-- Dependencies: 211
-- Name: tags_tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE tags_tag_id_seq OWNED BY tags.tag_id;


--
-- TOC entry 4351 (class 2604 OID 38315)
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY curvature_segments ALTER COLUMN id SET DEFAULT nextval('curvature_segments_id_seq'::regclass);


--
-- TOC entry 4353 (class 2604 OID 19831)
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY sources ALTER COLUMN id SET DEFAULT nextval('sources_id_seq'::regclass);


--
-- TOC entry 4354 (class 2604 OID 38117)
-- Name: tag_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY tags ALTER COLUMN tag_id SET DEFAULT nextval('tags_tag_id_seq'::regclass);


--
-- TOC entry 4358 (class 2606 OID 48190)
-- Name: curvature_segments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY curvature_segments
    ADD CONSTRAINT curvature_segments_pkey PRIMARY KEY (id);


--
-- TOC entry 4363 (class 2606 OID 48224)
-- Name: id_hash_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY curvature_segments
    ADD CONSTRAINT id_hash_unique UNIQUE (id_hash);


--
-- TOC entry 4368 (class 2606 OID 48188)
-- Name: segment_ways_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY segment_ways
    ADD CONSTRAINT segment_ways_pkey PRIMARY KEY (fk_segment, id);


--
-- TOC entry 4370 (class 2606 OID 19837)
-- Name: sources_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY sources
    ADD CONSTRAINT sources_pkey PRIMARY KEY (id);


--
-- TOC entry 4372 (class 2606 OID 38119)
-- Name: tag_primary_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tags
    ADD CONSTRAINT tag_primary_key PRIMARY KEY (tag_id);


--
-- TOC entry 4374 (class 2606 OID 38121)
-- Name: unique_name_value; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tags
    ADD CONSTRAINT unique_name_value UNIQUE (tag_name, tag_value);


--
-- TOC entry 4355 (class 1259 OID 19838)
-- Name: curvature_segment_geom; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX curvature_segment_geom ON curvature_segments USING gist (geom);


--
-- TOC entry 4356 (class 1259 OID 19839)
-- Name: curvature_segments_length_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX curvature_segments_length_idx ON curvature_segments USING btree (curvature, length);


--
-- TOC entry 4359 (class 1259 OID 19840)
-- Name: fki_foreign_key_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_foreign_key_source ON curvature_segments USING btree (fk_source);


--
-- TOC entry 4360 (class 1259 OID 38299)
-- Name: fki_highway_key; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_highway_key ON curvature_segments USING btree (fk_highway);


--
-- TOC entry 4365 (class 1259 OID 48216)
-- Name: fki_segment_ways_fk_highway_key; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_segment_ways_fk_highway_key ON segment_ways USING btree (fk_highway);


--
-- TOC entry 4366 (class 1259 OID 48222)
-- Name: fki_segment_ways_fk_surface_key; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_segment_ways_fk_surface_key ON segment_ways USING btree (fk_surface);


--
-- TOC entry 4361 (class 1259 OID 38293)
-- Name: fki_source_key; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_source_key ON curvature_segments USING btree (fk_surface);


--
-- TOC entry 4364 (class 1259 OID 19841)
-- Name: length_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX length_idx ON curvature_segments USING btree (length);


--
-- TOC entry 4376 (class 2606 OID 48269)
-- Name: fk_highway_key; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY curvature_segments
    ADD CONSTRAINT fk_highway_key FOREIGN KEY (fk_highway) REFERENCES tags(tag_id) ON DELETE RESTRICT;


--
-- TOC entry 4377 (class 2606 OID 48274)
-- Name: fk_source_key; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY curvature_segments
    ADD CONSTRAINT fk_source_key FOREIGN KEY (fk_surface) REFERENCES tags(tag_id) ON DELETE RESTRICT;


--
-- TOC entry 4375 (class 2606 OID 19848)
-- Name: foreign_key_source; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY curvature_segments
    ADD CONSTRAINT foreign_key_source FOREIGN KEY (fk_source) REFERENCES sources(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 4378 (class 2606 OID 48249)
-- Name: segment_ways_fk_highway_key; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY segment_ways
    ADD CONSTRAINT segment_ways_fk_highway_key FOREIGN KEY (fk_highway) REFERENCES tags(tag_id) ON DELETE RESTRICT;


--
-- TOC entry 4379 (class 2606 OID 48259)
-- Name: segment_ways_fk_segment_key; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY segment_ways
    ADD CONSTRAINT segment_ways_fk_segment_key FOREIGN KEY (fk_segment) REFERENCES curvature_segments(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 4380 (class 2606 OID 48264)
-- Name: segment_ways_fk_surface_key; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY segment_ways
    ADD CONSTRAINT segment_ways_fk_surface_key FOREIGN KEY (fk_surface) REFERENCES tags(tag_id) ON DELETE RESTRICT;


-- Completed on 2017-01-04 23:02:11 EST

--
-- PostgreSQL database dump complete
--

