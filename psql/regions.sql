--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3 (Debian 16.3-1.pgdg120+1)
-- Dumped by pg_dump version 16.3 (Ubuntu 16.3-1.pgdg22.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP TRIGGER on_update_current_timestamp ON public.regions;
ALTER TABLE ONLY public.regions DROP CONSTRAINT idx_16402_primary;
ALTER TABLE public.regions ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE public.regions_id_seq;
DROP TABLE public.regions;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: regions; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.regions (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    translations text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    flag boolean DEFAULT true NOT NULL,
    wikidataid character varying(255)
);


ALTER TABLE public.regions OWNER TO root;

--
-- Name: COLUMN regions.wikidataid; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.regions.wikidataid IS 'Rapid API GeoDB Cities';


--
-- Name: regions_id_seq; Type: SEQUENCE; Schema: public; Owner: root
--

CREATE SEQUENCE public.regions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.regions_id_seq OWNER TO root;

--
-- Name: regions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: root
--

ALTER SEQUENCE public.regions_id_seq OWNED BY public.regions.id;


--
-- Name: regions id; Type: DEFAULT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.regions ALTER COLUMN id SET DEFAULT nextval('public.regions_id_seq'::regclass);


--
-- Data for Name: regions; Type: TABLE DATA; Schema: public; Owner: root
--

INSERT INTO public.regions VALUES
	(1, 'Africa', '{"kr":"아프리카","pt-BR":"África","pt":"África","nl":"Afrika","hr":"Afrika","fa":"آفریقا","de":"Afrika","es":"África","fr":"Afrique","ja":"アフリカ","it":"Africa","cn":"非洲","tr":"Afrika"}', '2023-08-14 07:11:03+00', '2023-08-14 07:11:03+00', true, 'Q15'),
	(2, 'Americas', '{"kr":"아메리카","pt-BR":"América","pt":"América","nl":"Amerika","hr":"Amerika","fa":"قاره آمریکا","de":"Amerika","es":"América","fr":"Amérique","ja":"アメリカ州","it":"America","cn":"美洲","tr":"Amerika"}', '2023-08-14 07:11:03+00', '2023-08-14 07:11:03+00', true, 'Q828'),
	(3, 'Asia', '{"kr":"아시아","pt-BR":"Ásia","pt":"Ásia","nl":"Azië","hr":"Ázsia","fa":"آسیا","de":"Asien","es":"Asia","fr":"Asie","ja":"アジア","it":"Asia","cn":"亚洲","tr":"Asya"}', '2023-08-14 07:11:03+00', '2023-08-14 07:11:03+00', true, 'Q48'),
	(4, 'Europe', '{"kr":"유럽","pt-BR":"Europa","pt":"Europa","nl":"Europa","hr":"Európa","fa":"اروپا","de":"Europa","es":"Europa","fr":"Europe","ja":"ヨーロッパ","it":"Europa","cn":"欧洲","tr":"Avrupa"}', '2023-08-14 07:11:03+00', '2023-08-14 07:11:03+00', true, 'Q46'),
	(5, 'Oceania', '{"kr":"오세아니아","pt-BR":"Oceania","pt":"Oceania","nl":"Oceanië en Australië","hr":"Óceánia és Ausztrália","fa":"اقیانوسیه","de":"Ozeanien und Australien","es":"Oceanía","fr":"Océanie","ja":"オセアニア","it":"Oceania","cn":"大洋洲","tr":"Okyanusya"}', '2023-08-14 07:11:03+00', '2023-08-14 07:11:03+00', true, 'Q55643'),
	(6, 'Polar', '{"kr":"남극","pt-BR":"Antártida","pt":"Antártida","nl":"Antarctica","hr":"Antarktika","fa":"جنوبگان","de":"Antarktika","es":"Antártida","fr":"Antarctique","ja":"南極大陸","it":"Antartide","cn":"南極洲","tr":"Antarktika"}', '2023-08-14 07:11:03+00', '2023-08-14 07:11:03+00', true, 'Q51');


--
-- Name: regions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: root
--

SELECT pg_catalog.setval('public.regions_id_seq', 6, true);


--
-- Name: regions idx_16402_primary; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT idx_16402_primary PRIMARY KEY (id);


--
-- Name: regions on_update_current_timestamp; Type: TRIGGER; Schema: public; Owner: root
--

CREATE TRIGGER on_update_current_timestamp BEFORE UPDATE ON public.regions FOR EACH ROW EXECUTE FUNCTION public.on_update_current_timestamp_regions();


--
-- PostgreSQL database dump complete
--

