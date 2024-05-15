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

ALTER TABLE ONLY public.subregions DROP CONSTRAINT subregion_continent_final;
DROP TRIGGER on_update_current_timestamp ON public.subregions;
DROP INDEX public.idx_16418_subregion_continent;
ALTER TABLE ONLY public.subregions DROP CONSTRAINT idx_16418_primary;
ALTER TABLE public.subregions ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE public.subregions_id_seq;
DROP TABLE public.subregions;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: subregions; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.subregions (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    translations text,
    region_id integer NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    flag boolean DEFAULT true NOT NULL,
    wikidataid character varying(255)
);


ALTER TABLE public.subregions OWNER TO root;

--
-- Name: COLUMN subregions.wikidataid; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.subregions.wikidataid IS 'Rapid API GeoDB Cities';


--
-- Name: subregions_id_seq; Type: SEQUENCE; Schema: public; Owner: root
--

CREATE SEQUENCE public.subregions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subregions_id_seq OWNER TO root;

--
-- Name: subregions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: root
--

ALTER SEQUENCE public.subregions_id_seq OWNED BY public.subregions.id;


--
-- Name: subregions id; Type: DEFAULT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.subregions ALTER COLUMN id SET DEFAULT nextval('public.subregions_id_seq'::regclass);


--
-- Data for Name: subregions; Type: TABLE DATA; Schema: public; Owner: root
--

INSERT INTO public.subregions VALUES
	(1, 'Northern Africa', '{"korean":"북아프리카","portuguese":"Norte de África","dutch":"Noord-Afrika","croatian":"Sjeverna Afrika","persian":"شمال آفریقا","german":"Nordafrika","spanish":"Norte de África","french":"Afrique du Nord","japanese":"北アフリカ","italian":"Nordafrica","chinese":"北部非洲"}', 1, '2023-08-14 07:11:03+00', '2023-08-24 20:10:23+00', true, 'Q27381'),
	(2, 'Middle Africa', '{"korean":"중앙아프리카","portuguese":"África Central","dutch":"Centraal-Afrika","croatian":"Srednja Afrika","persian":"مرکز آفریقا","german":"Zentralafrika","spanish":"África Central","french":"Afrique centrale","japanese":"中部アフリカ","italian":"Africa centrale","chinese":"中部非洲"}', 1, '2023-08-14 07:11:03+00', '2023-08-24 20:22:09+00', true, 'Q27433'),
	(3, 'Western Africa', '{"korean":"서아프리카","portuguese":"África Ocidental","dutch":"West-Afrika","croatian":"Zapadna Afrika","persian":"غرب آفریقا","german":"Westafrika","spanish":"África Occidental","french":"Afrique de l''Ouest","japanese":"西アフリカ","italian":"Africa occidentale","chinese":"西非"}', 1, '2023-08-14 07:11:03+00', '2023-08-24 20:22:09+00', true, 'Q4412'),
	(4, 'Eastern Africa', '{"korean":"동아프리카","portuguese":"África Oriental","dutch":"Oost-Afrika","croatian":"Istočna Afrika","persian":"شرق آفریقا","german":"Ostafrika","spanish":"África Oriental","french":"Afrique de l''Est","japanese":"東アフリカ","italian":"Africa orientale","chinese":"东部非洲"}', 1, '2023-08-14 07:11:03+00', '2023-08-24 20:22:10+00', true, 'Q27407'),
	(5, 'Southern Africa', '{"korean":"남아프리카","portuguese":"África Austral","dutch":"Zuidelijk Afrika","croatian":"Južna Afrika","persian":"جنوب آفریقا","german":"Südafrika","spanish":"África austral","french":"Afrique australe","japanese":"南部アフリカ","italian":"Africa australe","chinese":"南部非洲"}', 1, '2023-08-14 07:11:03+00', '2023-08-24 20:22:10+00', true, 'Q27394'),
	(6, 'Northern America', '{"korean":"북미","portuguese":"América Setentrional","dutch":"Noord-Amerika","persian":"شمال آمریکا","german":"Nordamerika","spanish":"América Norteña","french":"Amérique septentrionale","japanese":"北部アメリカ","italian":"America settentrionale","chinese":"北美地區"}', 2, '2023-08-14 07:11:03+00', '2023-08-24 20:22:10+00', true, 'Q2017699'),
	(7, 'Caribbean', '{"korean":"카리브","portuguese":"Caraíbas","dutch":"Caraïben","croatian":"Karibi","persian":"کارائیب","german":"Karibik","spanish":"Caribe","french":"Caraïbes","japanese":"カリブ海地域","italian":"Caraibi","chinese":"加勒比地区"}', 2, '2023-08-14 07:11:03+00', '2023-08-24 20:22:10+00', true, 'Q664609'),
	(8, 'South America', '{"korean":"남아메리카","portuguese":"América do Sul","dutch":"Zuid-Amerika","croatian":"Južna Amerika","persian":"آمریکای جنوبی","german":"Südamerika","spanish":"América del Sur","french":"Amérique du Sud","japanese":"南アメリカ","italian":"America meridionale","chinese":"南美洲"}', 2, '2023-08-14 07:11:03+00', '2023-08-24 20:22:10+00', true, 'Q18'),
	(9, 'Central America', '{"korean":"중앙아메리카","portuguese":"América Central","dutch":"Centraal-Amerika","croatian":"Srednja Amerika","persian":"آمریکای مرکزی","german":"Zentralamerika","spanish":"América Central","french":"Amérique centrale","japanese":"中央アメリカ","italian":"America centrale","chinese":"中美洲"}', 2, '2023-08-14 07:11:03+00', '2023-08-24 20:22:11+00', true, 'Q27611'),
	(10, 'Central Asia', '{"korean":"중앙아시아","portuguese":"Ásia Central","dutch":"Centraal-Azië","croatian":"Srednja Azija","persian":"آسیای میانه","german":"Zentralasien","spanish":"Asia Central","french":"Asie centrale","japanese":"中央アジア","italian":"Asia centrale","chinese":"中亚"}', 3, '2023-08-14 07:11:03+00', '2023-08-24 20:22:11+00', true, 'Q27275'),
	(11, 'Western Asia', '{"korean":"서아시아","portuguese":"Sudoeste Asiático","dutch":"Zuidwest-Azië","croatian":"Jugozapadna Azija","persian":"غرب آسیا","german":"Vorderasien","spanish":"Asia Occidental","french":"Asie de l''Ouest","japanese":"西アジア","italian":"Asia occidentale","chinese":"西亚"}', 3, '2023-08-14 07:11:03+00', '2023-08-24 20:22:11+00', true, 'Q27293'),
	(12, 'Eastern Asia', '{"korean":"동아시아","portuguese":"Ásia Oriental","dutch":"Oost-Azië","croatian":"Istočna Azija","persian":"شرق آسیا","german":"Ostasien","spanish":"Asia Oriental","french":"Asie de l''Est","japanese":"東アジア","italian":"Asia orientale","chinese":"東亞"}', 3, '2023-08-14 07:11:03+00', '2023-08-24 20:22:11+00', true, 'Q27231'),
	(13, 'South-Eastern Asia', '{"korean":"동남아시아","portuguese":"Sudeste Asiático","dutch":"Zuidoost-Azië","croatian":"Jugoistočna Azija","persian":"جنوب شرق آسیا","german":"Südostasien","spanish":"Sudeste Asiático","french":"Asie du Sud-Est","japanese":"東南アジア","italian":"Sud-est asiatico","chinese":"东南亚"}', 3, '2023-08-14 07:11:03+00', '2023-08-24 20:22:12+00', true, 'Q11708'),
	(14, 'Southern Asia', '{"korean":"남아시아","portuguese":"Ásia Meridional","dutch":"Zuid-Azië","croatian":"Južna Azija","persian":"جنوب آسیا","german":"Südasien","spanish":"Asia del Sur","french":"Asie du Sud","japanese":"南アジア","italian":"Asia meridionale","chinese":"南亚"}', 3, '2023-08-14 07:11:03+00', '2023-08-24 20:22:12+00', true, 'Q771405'),
	(15, 'Eastern Europe', '{"korean":"동유럽","portuguese":"Europa de Leste","dutch":"Oost-Europa","croatian":"Istočna Europa","persian":"شرق اروپا","german":"Osteuropa","spanish":"Europa Oriental","french":"Europe de l''Est","japanese":"東ヨーロッパ","italian":"Europa orientale","chinese":"东欧"}', 4, '2023-08-14 07:11:03+00', '2023-08-24 20:22:12+00', true, 'Q27468'),
	(16, 'Southern Europe', '{"korean":"남유럽","portuguese":"Europa meridional","dutch":"Zuid-Europa","croatian":"Južna Europa","persian":"جنوب اروپا","german":"Südeuropa","spanish":"Europa del Sur","french":"Europe du Sud","japanese":"南ヨーロッパ","italian":"Europa meridionale","chinese":"南欧"}', 4, '2023-08-14 07:11:03+00', '2023-08-24 20:22:12+00', true, 'Q27449'),
	(17, 'Western Europe', '{"korean":"서유럽","portuguese":"Europa Ocidental","dutch":"West-Europa","croatian":"Zapadna Europa","persian":"غرب اروپا","german":"Westeuropa","spanish":"Europa Occidental","french":"Europe de l''Ouest","japanese":"西ヨーロッパ","italian":"Europa occidentale","chinese":"西欧"}', 4, '2023-08-14 07:11:03+00', '2023-08-24 20:22:12+00', true, 'Q27496'),
	(18, 'Northern Europe', '{"korean":"북유럽","portuguese":"Europa Setentrional","dutch":"Noord-Europa","croatian":"Sjeverna Europa","persian":"شمال اروپا","german":"Nordeuropa","spanish":"Europa del Norte","french":"Europe du Nord","japanese":"北ヨーロッパ","italian":"Europa settentrionale","chinese":"北歐"}', 4, '2023-08-14 07:11:03+00', '2023-08-24 20:22:13+00', true, 'Q27479'),
	(19, 'Australia and New Zealand', '{"korean":"오스트랄라시아","portuguese":"Australásia","dutch":"Australazië","croatian":"Australazija","persian":"استرالزی","german":"Australasien","spanish":"Australasia","french":"Australasie","japanese":"オーストララシア","italian":"Australasia","chinese":"澳大拉西亞"}', 5, '2023-08-14 07:11:03+00', '2023-08-24 20:22:13+00', true, 'Q45256'),
	(20, 'Melanesia', '{"korean":"멜라네시아","portuguese":"Melanésia","dutch":"Melanesië","croatian":"Melanezija","persian":"ملانزی","german":"Melanesien","spanish":"Melanesia","french":"Mélanésie","japanese":"メラネシア","italian":"Melanesia","chinese":"美拉尼西亚"}', 5, '2023-08-14 07:11:03+00', '2023-08-24 20:22:13+00', true, 'Q37394'),
	(21, 'Micronesia', '{"korean":"미크로네시아","portuguese":"Micronésia","dutch":"Micronesië","croatian":"Mikronezija","persian":"میکرونزی","german":"Mikronesien","spanish":"Micronesia","french":"Micronésie","japanese":"ミクロネシア","italian":"Micronesia","chinese":"密克罗尼西亚群岛"}', 5, '2023-08-14 07:11:03+00', '2023-08-24 20:22:13+00', true, 'Q3359409'),
	(22, 'Polynesia', '{"korean":"폴리네시아","portuguese":"Polinésia","dutch":"Polynesië","croatian":"Polinezija","persian":"پلی‌نزی","german":"Polynesien","spanish":"Polinesia","french":"Polynésie","japanese":"ポリネシア","italian":"Polinesia","chinese":"玻里尼西亞"}', 5, '2023-08-14 07:11:03+00', '2023-08-24 20:22:13+00', true, 'Q35942');


--
-- Name: subregions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: root
--

SELECT pg_catalog.setval('public.subregions_id_seq', 22, true);


--
-- Name: subregions idx_16418_primary; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.subregions
    ADD CONSTRAINT idx_16418_primary PRIMARY KEY (id);


--
-- Name: idx_16418_subregion_continent; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_16418_subregion_continent ON public.subregions USING btree (region_id);


--
-- Name: subregions on_update_current_timestamp; Type: TRIGGER; Schema: public; Owner: root
--

CREATE TRIGGER on_update_current_timestamp BEFORE UPDATE ON public.subregions FOR EACH ROW EXECUTE FUNCTION public.on_update_current_timestamp_subregions();


--
-- Name: subregions subregion_continent_final; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.subregions
    ADD CONSTRAINT subregion_continent_final FOREIGN KEY (region_id) REFERENCES public.regions(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

