--
-- PostgreSQL database dump
--


-- Dumped from database version 16.15 (Ubuntu 16.15-1.pgdg24.04+2)
-- Dumped by pg_dump version 16.15 (Ubuntu 16.15-1.pgdg24.04+2)

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

ALTER TABLE IF EXISTS ONLY public.county_states DROP CONSTRAINT IF EXISTS county_states_state_id_fkey;
ALTER TABLE IF EXISTS ONLY public.county_states DROP CONSTRAINT IF EXISTS county_states_county_id_fkey;
DROP INDEX IF EXISTS public.county_states_state_id_idx;
ALTER TABLE IF EXISTS ONLY public.county_states DROP CONSTRAINT IF EXISTS county_states_pkey;
DROP TABLE IF EXISTS public.county_states;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: county_states; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.county_states (
    county_id bigint NOT NULL,
    state_id bigint NOT NULL
);


--
-- Name: TABLE county_states; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.county_states IS 'Regions of a county of several regions (v5); a county with its own state has no rows';


--
-- Data for Name: county_states; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.county_states (county_id, state_id) VALUES
	(14023, 4060),
	(14024, 4060),
	(14026, 4060),
	(14027, 4060),
	(14028, 4060),
	(14023, 4061),
	(14024, 4061),
	(14025, 4061),
	(14029, 4062),
	(14028, 4065),
	(14029, 4066),
	(14026, 4069),
	(14024, 4074),
	(14025, 4074),
	(14024, 4075),
	(14027, 4075);


--
-- Name: county_states county_states_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.county_states
    ADD CONSTRAINT county_states_pkey PRIMARY KEY (county_id, state_id);


--
-- Name: county_states_state_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX county_states_state_id_idx ON public.county_states USING btree (state_id);


--
-- Name: county_states county_states_county_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.county_states
    ADD CONSTRAINT county_states_county_id_fkey FOREIGN KEY (county_id) REFERENCES public.counties(id) ON DELETE CASCADE;


--
-- Name: county_states county_states_state_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.county_states
    ADD CONSTRAINT county_states_state_id_fkey FOREIGN KEY (state_id) REFERENCES public.states(id);


--
-- PostgreSQL database dump complete
--


