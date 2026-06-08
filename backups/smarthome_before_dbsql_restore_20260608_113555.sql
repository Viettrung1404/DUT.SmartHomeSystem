--
-- PostgreSQL database dump
--

\restrict lft0csTHglggbChm7ckQiTXj8U35Jr5Al88KJ9XYwC07U0S4Mm1PZGxsDeiqD5q

-- Dumped from database version 17.7
-- Dumped by pg_dump version 17.7

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

-- *not* creating schema, since initdb creates it


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS '';


--
-- Name: actiontype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.actiontype AS ENUM (
    'SCHEDULE',
    'ALERT',
    'AUTOMATION'
);


--
-- Name: devicetype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.devicetype AS ENUM (
    'LIGHT',
    'FAN',
    'AC',
    'SENSOR',
    'CAMERA',
    'LOCK'
);


--
-- Name: eventtype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.eventtype AS ENUM (
    'DEVICE_ON',
    'DEVICE_OFF',
    'FACE_UNLOCK',
    'FORGOT_OFF',
    'SCENE_ON'
);


--
-- Name: metrictype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.metrictype AS ENUM (
    'TEMP',
    'HUMIDITY',
    'POWER_W',
    'VOLTAGE'
);


--
-- Name: patterntype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.patterntype AS ENUM (
    'CLUSTER',
    'TIME_HABIT',
    'CORRELATION',
    'ANOMALY'
);


--
-- Name: suggestionfeedbacktype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.suggestionfeedbacktype AS ENUM (
    'ACCEPT',
    'REJECT',
    'IGNORE'
);


--
-- Name: triggersource; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.triggersource AS ENUM (
    'USER',
    'SCHEDULE',
    'SENSOR',
    'AUTOMATION',
    'PHYSICAL_ATTRIBUTED',
    'PHYSICAL_UNKNOWN'
);


--
-- Name: userrole; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.userrole AS ENUM (
    'ADMIN',
    'MEMBER',
    'GUEST'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: activity_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.activity_logs (
    id integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    device_id uuid NOT NULL,
    user_id uuid,
    event_type public.eventtype NOT NULL,
    description text,
    session_end timestamp with time zone,
    duration_seconds integer,
    trigger_source public.triggersource NOT NULL,
    metadata jsonb,
    home_id uuid NOT NULL
);


--
-- Name: activity_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.activity_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: activity_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.activity_logs_id_seq OWNED BY public.activity_logs.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: auth_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_sessions (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    refresh_token_hash character varying NOT NULL,
    user_agent character varying,
    ip_address character varying,
    created_at timestamp with time zone NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    last_used_at timestamp with time zone,
    revoked_at timestamp with time zone
);


--
-- Name: automation_actions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.automation_actions (
    id uuid NOT NULL,
    automation_id uuid NOT NULL,
    device_id uuid,
    action character varying NOT NULL,
    value character varying
);


--
-- Name: automation_conditions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.automation_conditions (
    id uuid NOT NULL,
    automation_id uuid NOT NULL,
    condition_type character varying NOT NULL,
    value character varying NOT NULL
);


--
-- Name: automations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.automations (
    id uuid NOT NULL,
    home_id uuid NOT NULL,
    name character varying NOT NULL,
    enabled boolean NOT NULL,
    created_at timestamp without time zone NOT NULL
);


--
-- Name: device_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.device_logs (
    id uuid NOT NULL,
    device_id uuid NOT NULL,
    action character varying NOT NULL,
    value character varying,
    "timestamp" timestamp without time zone NOT NULL
);


--
-- Name: device_states; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.device_states (
    device_id uuid NOT NULL,
    is_online boolean,
    state jsonb NOT NULL,
    last_updated timestamp with time zone DEFAULT now()
);


--
-- Name: devices; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.devices (
    id uuid NOT NULL,
    slug character varying(100),
    room_id uuid,
    name character varying(100),
    type public.devicetype NOT NULL,
    mqtt_topic character varying(255) NOT NULL,
    config jsonb,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: energy_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.energy_logs (
    id uuid NOT NULL,
    device_id uuid NOT NULL,
    power_usage double precision NOT NULL,
    "timestamp" timestamp without time zone NOT NULL
);


--
-- Name: home_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.home_users (
    id integer NOT NULL,
    home_id uuid NOT NULL,
    user_id uuid NOT NULL,
    role public.userrole,
    joined_at timestamp with time zone DEFAULT now()
);


--
-- Name: home_users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.home_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: home_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.home_users_id_seq OWNED BY public.home_users.id;


--
-- Name: homes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.homes (
    id uuid NOT NULL,
    name character varying(100) NOT NULL,
    address character varying(255),
    timezone character varying(50),
    is_active boolean,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: password_reset_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.password_reset_tokens (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    token_hash character varying NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    used_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL
);


--
-- Name: rooms; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rooms (
    id uuid NOT NULL,
    name character varying(50) NOT NULL,
    icon character varying(50),
    image_url text,
    created_at timestamp with time zone DEFAULT now(),
    home_id uuid NOT NULL
);


--
-- Name: schedules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schedules (
    id integer NOT NULL,
    device_id uuid,
    name character varying(100),
    "time" time without time zone NOT NULL,
    days_of_week integer[],
    action_payload jsonb NOT NULL,
    is_active boolean,
    source_suggestion_id integer
);


--
-- Name: schedules_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.schedules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: schedules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.schedules_id_seq OWNED BY public.schedules.id;


--
-- Name: security_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.security_events (
    id uuid NOT NULL,
    home_id uuid NOT NULL,
    event_type character varying NOT NULL,
    severity character varying NOT NULL,
    description character varying NOT NULL,
    "timestamp" timestamp without time zone NOT NULL
);


--
-- Name: sensor_data; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sensor_data (
    "time" timestamp with time zone DEFAULT now() NOT NULL,
    device_id uuid NOT NULL,
    metric_type public.metrictype NOT NULL,
    value double precision NOT NULL
);


--
-- Name: suggestion_decision_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.suggestion_decision_logs (
    id integer NOT NULL,
    pattern_id integer NOT NULL,
    home_id uuid NOT NULL,
    user_id uuid NOT NULL,
    decision_score double precision NOT NULL,
    should_suggest boolean NOT NULL,
    blocked_by character varying(50),
    cooldown_signature character varying(255),
    metadata_json jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: suggestion_decision_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.suggestion_decision_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: suggestion_decision_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.suggestion_decision_logs_id_seq OWNED BY public.suggestion_decision_logs.id;


--
-- Name: suggestion_feedback_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.suggestion_feedback_logs (
    id integer NOT NULL,
    suggestion_id integer NOT NULL,
    user_id uuid NOT NULL,
    feedback_type public.suggestionfeedbacktype NOT NULL,
    feedback_reason text,
    feedback_time timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: suggestion_feedback_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.suggestion_feedback_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: suggestion_feedback_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.suggestion_feedback_logs_id_seq OWNED BY public.suggestion_feedback_logs.id;


--
-- Name: suggestion_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.suggestion_logs (
    id integer NOT NULL,
    user_id uuid NOT NULL,
    pattern_id integer,
    action_type public.actiontype NOT NULL,
    suggestion_text text NOT NULL,
    suggestion_json jsonb,
    was_accepted boolean,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: suggestion_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.suggestion_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: suggestion_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.suggestion_logs_id_seq OWNED BY public.suggestion_logs.id;


--
-- Name: user_patterns; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_patterns (
    id integer NOT NULL,
    user_id uuid NOT NULL,
    device_id uuid,
    pattern_type public.patterntype NOT NULL,
    pattern_data jsonb NOT NULL,
    confidence double precision,
    computed_at timestamp with time zone DEFAULT now(),
    is_active boolean,
    home_id uuid NOT NULL
);


--
-- Name: user_patterns_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_patterns_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_patterns_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_patterns_id_seq OWNED BY public.user_patterns.id;


--
-- Name: user_presence; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_presence (
    id integer NOT NULL,
    user_id uuid NOT NULL,
    room_id uuid,
    is_home boolean,
    detected_by character varying(20),
    last_seen timestamp with time zone DEFAULT now(),
    home_id uuid
);


--
-- Name: user_presence_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_presence_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_presence_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_presence_id_seq OWNED BY public.user_presence.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    email character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    full_name character varying(100),
    avatar_url text,
    role public.userrole,
    face_encoding double precision[],
    is_active boolean,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: activity_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activity_logs ALTER COLUMN id SET DEFAULT nextval('public.activity_logs_id_seq'::regclass);


--
-- Name: home_users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.home_users ALTER COLUMN id SET DEFAULT nextval('public.home_users_id_seq'::regclass);


--
-- Name: schedules id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedules ALTER COLUMN id SET DEFAULT nextval('public.schedules_id_seq'::regclass);


--
-- Name: suggestion_decision_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggestion_decision_logs ALTER COLUMN id SET DEFAULT nextval('public.suggestion_decision_logs_id_seq'::regclass);


--
-- Name: suggestion_feedback_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggestion_feedback_logs ALTER COLUMN id SET DEFAULT nextval('public.suggestion_feedback_logs_id_seq'::regclass);


--
-- Name: suggestion_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggestion_logs ALTER COLUMN id SET DEFAULT nextval('public.suggestion_logs_id_seq'::regclass);


--
-- Name: user_patterns id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_patterns ALTER COLUMN id SET DEFAULT nextval('public.user_patterns_id_seq'::regclass);


--
-- Name: user_presence id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_presence ALTER COLUMN id SET DEFAULT nextval('public.user_presence_id_seq'::regclass);


--
-- Data for Name: activity_logs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.activity_logs (id, "timestamp", device_id, user_id, event_type, description, session_end, duration_seconds, trigger_source, metadata, home_id) FROM stdin;
1	2026-04-07 23:02:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
2	2026-04-07 22:58:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-07 23:31:00+00	1980	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
3	2026-04-07 23:31:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
4	2026-04-07 23:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-07 23:54:00+00	1440	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
5	2026-04-07 23:54:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
6	2026-04-08 00:12:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
7	2026-04-08 13:09:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-08 15:53:00+00	9840	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
8	2026-04-08 15:53:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
9	2026-04-08 11:20:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-08 14:50:00+00	12600	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
10	2026-04-08 14:50:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
11	2026-04-08 12:23:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
12	2026-04-08 12:48:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-08 14:55:00+00	7620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
13	2026-04-08 14:55:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
14	2026-04-08 15:01:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
15	2026-04-08 15:50:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
16	2026-04-08 16:17:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
17	2026-04-08 06:18:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	FORGOT_OFF	\N	2026-04-08 09:32:00+00	11640	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
18	2026-04-08 06:23:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	FORGOT_OFF	\N	2026-04-08 09:14:00+00	10260	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
19	2026-04-07 23:44:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-08 00:11:00+00	1620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
20	2026-04-08 00:11:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
21	2026-04-07 23:47:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-08 00:25:00+00	2280	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
22	2026-04-08 00:25:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
23	2026-04-08 02:24:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-08 08:11:00+00	20820	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
24	2026-04-08 08:11:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
25	2026-04-08 03:41:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-08 03:56:00+00	900	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
26	2026-04-08 03:56:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
27	2026-04-08 07:55:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
28	2026-04-08 12:24:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-08 13:41:00+00	4620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
29	2026-04-08 13:41:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
30	2026-04-08 14:25:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-08 14:53:00+00	1680	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
31	2026-04-08 14:53:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
32	2026-04-08 15:04:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
33	2026-04-08 15:11:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
34	2026-04-09 02:29:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-09 03:09:00+00	2400	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
35	2026-04-09 03:09:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
36	2026-04-09 03:29:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-09 03:55:00+00	1560	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
37	2026-04-09 03:55:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
38	2026-04-09 02:30:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-09 06:56:00+00	15960	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
39	2026-04-09 06:56:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
40	2026-04-09 02:40:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-09 07:09:00+00	16140	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
41	2026-04-09 07:09:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
42	2026-04-09 05:00:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-09 05:41:00+00	2460	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
43	2026-04-09 05:41:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
44	2026-04-09 12:00:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-09 14:57:00+00	10620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
45	2026-04-09 14:57:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
46	2026-04-09 15:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-09 15:40:00+00	2400	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
47	2026-04-09 15:40:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
48	2026-04-09 15:10:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-09 17:06:00+00	6960	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
49	2026-04-09 17:06:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
50	2026-04-09 02:22:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
51	2026-04-09 02:27:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-09 06:39:00+00	15120	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
52	2026-04-09 06:39:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
53	2026-04-09 04:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-09 05:11:00+00	2460	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
54	2026-04-09 05:11:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
55	2026-04-09 08:09:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-09 11:17:00+00	11280	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
56	2026-04-09 11:17:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
57	2026-04-08 23:43:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-09 00:15:00+00	1920	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
58	2026-04-09 00:15:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
59	2026-04-08 23:57:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-09 00:28:00+00	1860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
60	2026-04-09 00:28:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
61	2026-04-09 03:12:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
62	2026-04-09 04:37:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-09 05:28:00+00	3060	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
63	2026-04-09 05:28:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
64	2026-04-09 06:00:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-09 07:33:00+00	5580	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
65	2026-04-09 07:33:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
66	2026-04-09 08:28:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-09 10:47:00+00	8340	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
67	2026-04-09 10:47:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
68	2026-04-09 14:18:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-09 14:48:00+00	1800	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
69	2026-04-09 14:48:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
70	2026-04-09 14:04:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-09 14:36:00+00	1920	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
71	2026-04-09 14:36:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
72	2026-04-09 23:04:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-09 23:39:00+00	2100	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
73	2026-04-09 23:39:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
74	2026-04-09 23:26:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-09 23:54:00+00	1680	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
75	2026-04-09 23:54:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
76	2026-04-09 23:41:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
77	2026-04-10 11:18:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-10 14:12:00+00	10440	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
78	2026-04-10 14:12:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
79	2026-04-10 15:34:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-10 16:07:00+00	1980	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
80	2026-04-10 16:07:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
81	2026-04-10 12:22:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-10 14:13:00+00	6660	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
82	2026-04-10 14:13:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
83	2026-04-10 16:51:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-10 17:40:00+00	2940	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
84	2026-04-10 17:40:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
85	2026-04-10 15:29:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-10 16:44:00+00	4500	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
86	2026-04-10 16:44:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
87	2026-04-10 15:37:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
88	2026-04-10 16:53:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
89	2026-04-10 07:02:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-10 09:35:00+00	9180	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
90	2026-04-10 09:35:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
91	2026-04-10 07:07:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-10 09:18:00+00	7860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
92	2026-04-10 09:18:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
93	2026-04-10 09:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-10 10:14:00+00	2640	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
94	2026-04-10 10:14:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
95	2026-04-11 00:40:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-11 01:42:00+00	3720	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
96	2026-04-11 01:42:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
97	2026-04-11 01:45:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-11 03:47:00+00	7320	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
98	2026-04-11 03:47:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
99	2026-04-11 11:21:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-11 15:37:00+00	15360	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
100	2026-04-11 15:37:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
101	2026-04-11 16:15:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-11 17:20:00+00	3900	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
102	2026-04-11 17:20:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
103	2026-04-11 01:31:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-11 02:38:00+00	4020	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
104	2026-04-11 02:38:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
105	2026-04-11 02:43:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-11 07:00:00+00	15420	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
106	2026-04-11 07:00:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
107	2026-04-11 02:26:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
108	2026-04-11 15:53:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-11 16:21:00+00	1680	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
109	2026-04-11 16:21:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
110	2026-04-11 15:16:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-11 16:52:00+00	5760	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
111	2026-04-11 16:52:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
112	2026-04-11 20:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-11 20:36:00+00	2160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
113	2026-04-11 20:36:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
114	2026-04-12 00:50:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-12 01:59:00+00	4140	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
115	2026-04-12 01:59:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
116	2026-04-12 01:45:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-12 02:28:00+00	2580	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
117	2026-04-12 02:28:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
118	2026-04-12 02:13:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-12 03:45:00+00	5520	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
119	2026-04-12 03:45:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
120	2026-04-12 13:01:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-12 15:04:00+00	7380	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
121	2026-04-12 15:04:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
122	2026-04-12 11:34:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-12 15:22:00+00	13680	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
123	2026-04-12 15:22:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
124	2026-04-12 12:10:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-12 15:49:00+00	13140	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
125	2026-04-12 15:49:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
126	2026-04-12 16:30:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-12 17:29:00+00	3540	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
127	2026-04-12 17:29:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
128	2026-04-11 19:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-11 19:19:00+00	1140	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
129	2026-04-11 19:19:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
130	2026-04-12 01:38:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-12 02:43:00+00	3900	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
131	2026-04-12 02:43:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
132	2026-04-12 02:18:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-12 07:06:00+00	17280	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
133	2026-04-12 07:06:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
134	2026-04-12 15:41:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
135	2026-04-12 15:32:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
136	2026-04-12 23:10:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-12 23:55:00+00	2700	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
137	2026-04-12 23:55:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
138	2026-04-12 23:11:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-12 23:46:00+00	2100	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
139	2026-04-12 23:46:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
140	2026-04-12 23:49:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-13 00:12:00+00	1380	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
141	2026-04-13 00:12:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
142	2026-04-13 00:16:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
143	2026-04-13 00:18:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
144	2026-04-13 13:59:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-13 17:07:00+00	11280	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
145	2026-04-13 17:07:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
146	2026-04-13 11:20:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-13 14:24:00+00	11040	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
147	2026-04-13 14:24:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
148	2026-04-13 11:52:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
149	2026-04-13 16:38:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-13 18:03:00+00	5100	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
150	2026-04-13 18:03:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
151	2026-04-13 16:31:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
152	2026-04-13 16:23:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
153	2026-04-12 23:53:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-13 00:25:00+00	1920	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
154	2026-04-13 00:25:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
155	2026-04-13 01:55:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-13 05:45:00+00	13800	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
156	2026-04-13 05:45:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
157	2026-04-13 04:16:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-13 05:09:00+00	3180	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
158	2026-04-13 05:09:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
159	2026-04-13 06:11:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-13 07:19:00+00	4080	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
160	2026-04-13 07:19:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
161	2026-04-13 07:27:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-13 09:26:00+00	7140	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
162	2026-04-13 09:26:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
163	2026-04-13 08:15:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-13 10:46:00+00	9060	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
164	2026-04-13 10:46:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
165	2026-04-13 12:53:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-13 14:42:00+00	6540	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
166	2026-04-13 14:42:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
167	2026-04-13 14:09:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-13 14:42:00+00	1980	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
168	2026-04-13 14:42:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
169	2026-04-13 14:57:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
170	2026-04-14 01:22:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-14 02:07:00+00	2700	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
171	2026-04-14 02:07:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
172	2026-04-14 02:22:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-14 02:54:00+00	1920	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
173	2026-04-14 02:54:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
174	2026-04-14 02:30:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-14 06:52:00+00	15720	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
175	2026-04-14 06:52:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
176	2026-04-14 02:40:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-14 08:13:00+00	19980	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
177	2026-04-14 08:13:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
178	2026-04-14 05:00:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-14 05:39:00+00	2340	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
179	2026-04-14 05:39:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
180	2026-04-14 12:00:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-14 14:24:00+00	8640	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
181	2026-04-14 14:24:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
182	2026-04-14 15:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-14 15:55:00+00	3300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
183	2026-04-14 15:55:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
184	2026-04-14 15:10:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-14 16:28:00+00	4680	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
185	2026-04-14 16:28:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
186	2026-04-13 22:54:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-13 23:25:00+00	1860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
187	2026-04-13 23:25:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
188	2026-04-14 03:32:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-14 03:48:00+00	960	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
189	2026-04-14 03:48:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
190	2026-04-14 04:31:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-14 05:21:00+00	3000	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
191	2026-04-14 05:21:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
192	2026-04-14 05:55:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-14 07:16:00+00	4860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
193	2026-04-14 07:16:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
194	2026-04-14 07:43:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
195	2026-04-14 06:39:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-14 08:38:00+00	7140	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
196	2026-04-14 08:38:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
197	2026-04-14 09:55:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-14 11:01:00+00	3960	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
198	2026-04-14 11:01:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
199	2026-04-14 12:20:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-14 13:55:00+00	5700	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
200	2026-04-14 13:55:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
201	2026-04-14 14:28:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-14 14:58:00+00	1800	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
202	2026-04-14 14:58:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
203	2026-04-14 14:15:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
204	2026-04-14 15:15:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
205	2026-04-14 13:44:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
206	2026-04-14 13:24:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-14 14:24:00+00	3600	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
207	2026-04-14 14:24:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
208	2026-04-16 14:00:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-16 17:29:00+00	12540	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
209	2026-04-16 17:29:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
210	2026-04-16 14:00:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-16 17:55:00+00	14100	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
211	2026-04-16 17:55:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
212	2026-04-15 23:50:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-16 00:18:00+00	1680	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
213	2026-04-16 00:18:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
214	2026-04-16 11:34:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-16 14:34:00+00	10800	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
215	2026-04-16 14:34:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
216	2026-04-16 15:57:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
217	2026-04-16 15:08:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-16 16:30:00+00	4920	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
218	2026-04-16 16:30:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
219	2026-04-16 15:42:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-16 17:00:00+00	4680	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
220	2026-04-16 17:00:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
221	2026-04-16 02:38:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-16 06:17:00+00	13140	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
222	2026-04-16 06:17:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
223	2026-04-16 02:43:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-16 06:52:00+00	14940	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
224	2026-04-16 06:52:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
225	2026-04-16 04:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-16 05:03:00+00	1980	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
226	2026-04-16 05:03:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
227	2026-04-16 07:24:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
228	2026-04-18 14:00:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
229	2026-04-18 14:00:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-18 20:29:00+00	23340	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
230	2026-04-18 20:29:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
231	2026-04-17 19:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-17 19:58:00+00	3480	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
232	2026-04-17 19:58:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
233	2026-04-18 00:07:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
234	2026-04-18 01:07:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-18 02:07:00+00	3600	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
235	2026-04-18 02:07:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
236	2026-04-18 01:25:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-18 01:56:00+00	1860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
237	2026-04-18 01:56:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
238	2026-04-18 12:53:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-18 14:54:00+00	7260	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
239	2026-04-18 14:54:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
240	2026-04-18 16:36:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
241	2026-04-18 16:50:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-18 18:31:00+00	6060	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
242	2026-04-18 18:31:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
243	2026-04-17 23:34:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-18 00:00:00+00	1560	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
244	2026-04-18 00:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
245	2026-04-18 02:14:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
246	2026-04-18 15:48:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-18 16:24:00+00	2160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
247	2026-04-18 16:24:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
248	2026-04-18 15:35:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-18 17:18:00+00	6180	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
249	2026-04-18 17:18:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
250	2026-04-19 00:45:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-19 01:47:00+00	3720	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
251	2026-04-19 01:47:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
252	2026-04-19 01:06:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-19 01:56:00+00	3000	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
253	2026-04-19 01:56:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
254	2026-04-19 01:27:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-19 02:11:00+00	2640	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
255	2026-04-19 02:11:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
256	2026-04-19 01:51:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-19 03:59:00+00	7680	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
257	2026-04-19 03:59:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
258	2026-04-19 12:21:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-19 14:19:00+00	7080	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
259	2026-04-19 14:19:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
260	2026-04-19 16:38:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-19 17:49:00+00	4260	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
261	2026-04-19 17:49:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
262	2026-04-19 16:21:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-19 17:51:00+00	5400	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
263	2026-04-19 17:51:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
264	2026-04-18 23:20:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-18 23:45:00+00	1500	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
265	2026-04-18 23:45:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
266	2026-04-19 01:47:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-19 02:34:00+00	2820	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
267	2026-04-19 02:34:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
268	2026-04-19 02:34:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-19 06:43:00+00	14940	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
269	2026-04-19 06:43:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
270	2026-04-19 02:22:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-19 06:52:00+00	16200	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
271	2026-04-19 06:52:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
272	2026-04-19 06:22:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-19 09:20:00+00	10680	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
273	2026-04-19 09:20:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
274	2026-04-19 15:41:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-19 16:06:00+00	1500	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
275	2026-04-19 16:06:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
276	2026-04-20 14:00:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-20 18:41:00+00	16860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
277	2026-04-20 18:41:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
278	2026-04-20 14:00:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-20 19:56:00+00	21360	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
279	2026-04-20 19:56:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
280	2026-04-19 22:53:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-19 23:49:00+00	3360	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
281	2026-04-19 23:49:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
282	2026-04-19 23:29:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	FORGOT_OFF	\N	2026-04-20 02:19:00+00	10200	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
283	2026-04-20 00:34:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
284	2026-04-20 14:07:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-20 16:55:00+00	10080	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
285	2026-04-20 16:55:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
286	2026-04-20 11:15:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-20 13:54:00+00	9540	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
287	2026-04-20 13:54:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
288	2026-04-20 12:11:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	FORGOT_OFF	\N	2026-04-20 14:18:00+00	7620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
289	2026-04-20 16:37:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-20 17:46:00+00	4140	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
290	2026-04-20 17:46:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
291	2026-04-20 15:59:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
292	2026-04-20 15:46:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
293	2026-04-20 14:25:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-20 14:30:00+00	300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
294	2026-04-20 14:30:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
295	2026-04-20 15:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-20 18:21:00+00	12060	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
296	2026-04-20 18:21:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
297	2026-04-20 15:05:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-20 18:12:00+00	11220	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
298	2026-04-20 18:12:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
299	2026-04-19 23:18:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-19 23:51:00+00	1980	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
300	2026-04-19 23:51:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
301	2026-04-20 01:41:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-20 05:37:00+00	14160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
302	2026-04-20 05:37:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
303	2026-04-20 01:52:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-20 06:32:00+00	16800	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
304	2026-04-20 06:32:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
305	2026-04-20 03:20:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-20 03:37:00+00	1020	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
306	2026-04-20 03:37:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
307	2026-04-20 04:39:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-20 05:25:00+00	2760	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
308	2026-04-20 05:25:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
309	2026-04-20 07:37:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-20 10:44:00+00	11220	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
310	2026-04-20 10:44:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
311	2026-04-20 06:40:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-20 09:05:00+00	8700	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
312	2026-04-20 09:05:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
313	2026-04-20 10:12:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
314	2026-04-20 12:34:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
315	2026-04-20 14:39:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-20 15:01:00+00	1320	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
316	2026-04-20 15:01:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
317	2026-04-20 14:53:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
318	2026-04-20 06:58:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-20 07:16:00+00	1080	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
319	2026-04-20 07:16:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
320	2026-04-21 11:30:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-21 14:48:00+00	11880	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
321	2026-04-21 14:48:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
322	2026-04-21 16:59:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-21 17:41:00+00	2520	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
323	2026-04-21 17:41:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
324	2026-04-20 20:55:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
325	2026-04-20 20:58:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-20 21:41:00+00	2580	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
326	2026-04-20 21:41:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
327	2026-04-21 04:51:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-21 05:25:00+00	2040	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
328	2026-04-21 05:25:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
329	2026-04-20 18:49:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-20 20:03:00+00	4440	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
330	2026-04-20 20:03:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
331	2026-04-20 22:59:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-21 00:31:00+00	5520	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
332	2026-04-21 00:31:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
333	2026-04-20 19:55:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
334	2026-04-21 23:11:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-21 23:59:00+00	2880	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
335	2026-04-21 23:59:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
336	2026-04-21 23:48:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-22 00:15:00+00	1620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
337	2026-04-22 00:15:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
338	2026-04-21 23:58:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
339	2026-04-22 00:35:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
340	2026-04-22 14:15:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	FORGOT_OFF	\N	2026-04-22 21:10:00+00	24900	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
341	2026-04-22 14:53:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-22 15:46:00+00	3180	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
342	2026-04-22 15:46:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
343	2026-04-22 13:03:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-22 14:41:00+00	5880	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
344	2026-04-22 14:41:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
345	2026-04-22 15:03:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-22 15:57:00+00	3240	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
346	2026-04-22 15:57:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
347	2026-04-22 16:02:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
348	2026-04-21 23:34:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-22 00:06:00+00	1920	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
349	2026-04-22 00:06:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
350	2026-04-22 00:01:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
351	2026-04-22 02:15:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-22 05:00:00+00	9900	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
352	2026-04-22 05:00:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
353	2026-04-22 03:08:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-22 03:26:00+00	1080	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
354	2026-04-22 03:26:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
355	2026-04-22 04:47:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-22 05:42:00+00	3300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
356	2026-04-22 05:42:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
357	2026-04-22 05:32:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-22 06:40:00+00	4080	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
358	2026-04-22 06:40:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
359	2026-04-22 07:09:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
360	2026-04-22 07:14:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
361	2026-04-22 10:40:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-22 11:31:00+00	3060	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
362	2026-04-22 11:31:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
363	2026-04-22 12:11:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-22 14:03:00+00	6720	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
364	2026-04-22 14:03:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
365	2026-04-22 15:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
366	2026-04-23 14:00:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-23 18:52:00+00	17520	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
367	2026-04-23 18:52:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
368	2026-04-23 14:00:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-23 18:09:00+00	14940	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
369	2026-04-23 18:09:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
370	2026-04-22 23:07:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-22 23:56:00+00	2940	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
371	2026-04-22 23:56:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
372	2026-04-22 23:08:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-22 23:46:00+00	2280	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
373	2026-04-22 23:46:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
374	2026-04-22 23:12:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-22 23:36:00+00	1440	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
375	2026-04-22 23:36:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
376	2026-04-23 00:22:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
377	2026-04-23 13:22:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-23 16:01:00+00	9540	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
378	2026-04-23 16:01:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
379	2026-04-23 11:23:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
380	2026-04-23 11:46:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-23 12:34:00+00	2880	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
381	2026-04-23 12:34:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
382	2026-04-23 16:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-23 16:51:00+00	3060	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
383	2026-04-23 16:51:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
384	2026-04-23 15:56:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-23 17:23:00+00	5220	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
385	2026-04-23 17:23:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
386	2026-04-23 15:57:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
387	2026-04-23 15:49:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
388	2026-04-23 01:55:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-23 06:02:00+00	14820	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
389	2026-04-23 06:02:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
390	2026-04-23 01:00:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-23 04:53:00+00	13980	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
391	2026-04-23 04:53:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
392	2026-04-23 04:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-23 05:11:00+00	2460	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
393	2026-04-23 05:11:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
394	2026-04-23 08:01:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-23 10:29:00+00	8880	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
395	2026-04-23 10:29:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
396	2026-04-23 03:46:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-23 04:02:00+00	960	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
397	2026-04-23 04:02:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
398	2026-04-23 10:16:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-23 11:11:00+00	3300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
399	2026-04-23 11:11:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
400	2026-04-23 14:04:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-23 14:28:00+00	1440	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
401	2026-04-23 14:28:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
402	2026-04-23 14:54:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-23 15:21:00+00	1620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
403	2026-04-23 15:21:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
404	2026-04-23 14:44:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
405	2026-04-23 14:22:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-23 14:37:00+00	900	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
406	2026-04-23 14:37:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
407	2026-04-23 14:26:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-23 15:47:00+00	4860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
408	2026-04-23 15:47:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
409	2026-04-24 11:47:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-24 12:41:00+00	3240	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
410	2026-04-24 12:41:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
411	2026-04-24 14:51:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-24 15:34:00+00	2580	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
412	2026-04-24 15:34:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
413	2026-04-24 15:03:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
414	2026-04-23 18:45:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-23 21:08:00+00	8580	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
415	2026-04-23 21:08:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
416	2026-04-23 18:07:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-23 18:56:00+00	2940	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
417	2026-04-23 18:56:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
418	2026-04-24 07:35:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-24 09:30:00+00	6900	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
419	2026-04-24 09:30:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
420	2026-04-24 07:40:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-24 09:30:00+00	6600	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
421	2026-04-24 09:30:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
422	2026-04-24 09:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-24 10:03:00+00	1980	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
423	2026-04-24 10:03:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
424	2026-04-25 00:58:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-25 01:55:00+00	3420	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
425	2026-04-25 01:55:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
426	2026-04-25 00:59:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-25 01:51:00+00	3120	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
427	2026-04-25 01:51:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
428	2026-04-25 01:41:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-25 03:23:00+00	6120	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
429	2026-04-25 03:23:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
430	2026-04-25 12:38:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-25 14:25:00+00	6420	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
431	2026-04-25 14:25:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
432	2026-04-25 11:44:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-25 15:25:00+00	13260	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
433	2026-04-25 15:25:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
434	2026-04-25 12:05:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-25 14:56:00+00	10260	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
435	2026-04-25 14:56:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
436	2026-04-25 16:44:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
437	2026-04-25 09:18:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-25 09:23:00+00	300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
438	2026-04-25 09:23:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
439	2026-04-25 06:52:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-25 08:36:00+00	6240	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
440	2026-04-25 08:36:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
441	2026-04-25 15:43:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
442	2026-04-25 15:51:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-25 16:58:00+00	4020	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
443	2026-04-25 16:58:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
444	2026-04-26 14:00:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-26 20:01:00+00	21660	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
445	2026-04-26 20:01:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
446	2026-04-26 14:00:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-26 18:38:00+00	16680	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
447	2026-04-26 18:38:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
448	2026-04-26 00:44:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-26 01:26:00+00	2520	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
449	2026-04-26 01:26:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
450	2026-04-26 01:41:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-26 02:27:00+00	2760	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
451	2026-04-26 02:27:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
452	2026-04-26 02:10:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-26 04:37:00+00	8820	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
453	2026-04-26 04:37:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
454	2026-04-26 11:28:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
455	2026-04-26 16:17:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
456	2026-04-26 16:39:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-26 18:01:00+00	4920	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
457	2026-04-26 18:01:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
458	2026-04-25 23:44:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
459	2026-04-26 01:16:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-26 02:04:00+00	2880	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
460	2026-04-26 02:04:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
461	2026-04-26 14:53:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-26 15:11:00+00	1080	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
462	2026-04-26 15:11:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
463	2026-04-26 23:14:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-27 00:00:00+00	2760	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
464	2026-04-27 00:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
465	2026-04-26 19:35:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-26 20:51:00+00	4560	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
466	2026-04-26 20:51:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
467	2026-04-26 21:15:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-26 22:21:00+00	3960	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
468	2026-04-26 22:21:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
469	2026-04-26 17:06:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-26 18:25:00+00	4740	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
470	2026-04-26 18:25:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
471	2026-04-26 17:43:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
472	2026-04-27 23:23:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
473	2026-04-27 23:56:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
474	2026-04-28 14:22:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	FORGOT_OFF	\N	2026-04-28 20:39:00+00	22620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
475	2026-04-28 14:55:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-28 15:45:00+00	3000	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
476	2026-04-28 15:45:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
477	2026-04-28 15:40:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-28 17:09:00+00	5340	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
478	2026-04-28 17:09:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
479	2026-04-28 15:54:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
480	2026-04-28 01:31:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-28 05:18:00+00	13620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
481	2026-04-28 05:18:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
482	2026-04-28 01:36:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-28 05:49:00+00	15180	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
483	2026-04-28 05:49:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
484	2026-04-28 04:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-28 05:10:00+00	2400	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
485	2026-04-28 05:10:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
486	2026-04-28 06:28:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-28 08:57:00+00	8940	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
487	2026-04-28 08:57:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
488	2026-04-28 05:56:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	FORGOT_OFF	\N	2026-04-28 08:43:00+00	10020	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
489	2026-04-28 05:01:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	FORGOT_OFF	\N	2026-04-28 08:15:00+00	11640	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
490	2026-04-28 04:38:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-28 05:39:00+00	3660	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
491	2026-04-28 05:39:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
492	2026-04-28 12:16:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-28 13:24:00+00	4080	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
493	2026-04-28 13:24:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
494	2026-04-28 19:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-28 19:43:00+00	2580	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
495	2026-04-28 19:43:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
496	2026-04-29 23:11:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-29 23:52:00+00	2460	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
497	2026-04-29 23:52:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
498	2026-04-30 10:58:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-30 14:24:00+00	12360	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
499	2026-04-30 14:24:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
500	2026-04-30 12:00:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-30 12:45:00+00	2700	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
501	2026-04-30 12:45:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
502	2026-04-30 15:39:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-30 17:10:00+00	5460	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
503	2026-04-30 17:10:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
504	2026-04-30 16:26:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-30 17:04:00+00	2280	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
505	2026-04-30 17:04:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
506	2026-04-30 15:39:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-30 16:56:00+00	4620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
507	2026-04-30 16:56:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
508	2026-04-30 01:35:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-30 05:20:00+00	13500	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
509	2026-04-30 05:20:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
510	2026-04-30 01:40:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-30 06:39:00+00	17940	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
511	2026-04-30 06:39:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
512	2026-04-30 04:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-30 05:24:00+00	3240	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
513	2026-04-30 05:24:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
514	2026-04-30 09:17:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
515	2026-04-29 23:48:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-30 00:30:00+00	2520	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
516	2026-04-30 00:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
517	2026-04-30 05:41:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
518	2026-04-30 05:44:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-30 06:41:00+00	3420	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
519	2026-04-30 06:41:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
520	2026-04-30 10:02:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
521	2026-04-30 10:04:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-30 11:21:00+00	4620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
522	2026-04-30 11:21:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
523	2026-04-30 12:51:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-30 14:36:00+00	6300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
524	2026-04-30 14:36:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
525	2026-04-30 14:20:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-30 14:52:00+00	1920	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
526	2026-04-30 14:52:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
527	2026-04-30 14:22:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-30 14:48:00+00	1560	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
528	2026-04-30 14:48:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
529	2026-04-30 11:38:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-04-30 11:43:00+00	300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
530	2026-04-30 11:43:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
531	2026-04-30 23:01:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-30 23:58:00+00	3420	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
532	2026-04-30 23:58:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
533	2026-04-30 23:10:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-30 23:42:00+00	1920	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
534	2026-04-30 23:42:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
535	2026-04-30 23:24:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-04-30 23:49:00+00	1500	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
536	2026-04-30 23:49:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
537	2026-05-01 00:21:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
538	2026-05-01 00:28:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
539	2026-05-01 11:06:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-01 13:54:00+00	10080	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
540	2026-05-01 13:54:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
541	2026-05-01 14:44:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-01 15:40:00+00	3360	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
542	2026-05-01 15:40:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
543	2026-05-01 15:58:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
544	2026-05-01 16:44:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-01 18:15:00+00	5460	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
545	2026-05-01 18:15:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
546	2026-05-01 16:57:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
547	2026-05-01 16:17:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
548	2026-05-01 05:34:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-01 05:39:00+00	300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
549	2026-05-01 05:39:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
550	2026-05-01 07:37:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
551	2026-05-01 07:42:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
552	2026-05-01 09:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-01 10:05:00+00	2100	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
553	2026-05-01 10:05:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
554	2026-05-02 00:58:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-02 01:59:00+00	3660	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
555	2026-05-02 01:59:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
556	2026-05-02 01:35:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-02 02:15:00+00	2400	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
557	2026-05-02 02:15:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
558	2026-05-02 13:44:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-02 15:52:00+00	7680	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
559	2026-05-02 15:52:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
560	2026-05-02 12:00:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-02 14:17:00+00	8220	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
561	2026-05-02 14:17:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
562	2026-05-02 16:35:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-02 17:40:00+00	3900	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
563	2026-05-02 17:40:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
564	2026-05-02 16:50:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-02 18:12:00+00	4920	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
565	2026-05-02 18:12:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
566	2026-05-01 20:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-01 20:36:00+00	2160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
567	2026-05-01 20:36:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
568	2026-05-02 01:17:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-02 02:03:00+00	2760	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
569	2026-05-02 02:03:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
570	2026-05-02 03:07:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	FORGOT_OFF	\N	2026-05-02 09:07:00+00	21600	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
571	2026-05-02 03:03:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-02 08:23:00+00	19200	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
572	2026-05-02 08:23:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
573	2026-05-02 15:35:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
574	2026-05-03 00:57:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-03 01:54:00+00	3420	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
575	2026-05-03 01:54:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
576	2026-05-03 00:50:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-03 01:42:00+00	3120	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
577	2026-05-03 01:42:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
578	2026-05-03 01:37:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-03 02:18:00+00	2460	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
579	2026-05-03 02:18:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
580	2026-05-03 12:42:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-03 14:27:00+00	6300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
581	2026-05-03 14:27:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
582	2026-05-03 11:16:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-03 14:21:00+00	11100	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
583	2026-05-03 14:21:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
584	2026-05-03 16:47:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-03 17:31:00+00	2640	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
585	2026-05-03 17:31:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
586	2026-05-03 16:51:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-03 18:15:00+00	5040	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
587	2026-05-03 18:15:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
588	2026-05-03 01:53:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-03 02:58:00+00	3900	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
589	2026-05-03 02:58:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
590	2026-05-03 02:25:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-03 07:26:00+00	18060	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
591	2026-05-03 07:26:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
592	2026-05-03 06:54:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
593	2026-05-03 22:37:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-04 00:42:00+00	7500	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
594	2026-05-04 00:42:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
595	2026-05-03 17:30:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-03 18:08:00+00	2280	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
596	2026-05-03 18:08:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
597	2026-05-04 03:08:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
598	2026-05-04 03:13:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-04 07:06:00+00	13980	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
599	2026-05-04 07:06:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
600	2026-05-04 04:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-04 05:15:00+00	2700	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
601	2026-05-04 05:15:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
602	2026-05-04 07:33:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-04 10:19:00+00	9960	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
603	2026-05-03 21:11:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-03 22:24:00+00	4380	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
604	2026-05-03 22:24:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
605	2026-05-03 17:16:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-03 19:13:00+00	7020	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
606	2026-05-03 19:13:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
607	2026-05-03 20:39:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-03 21:39:00+00	3600	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
608	2026-05-03 21:39:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
609	2026-05-04 22:54:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-04 23:39:00+00	2700	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
610	2026-05-04 23:39:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
611	2026-05-04 23:13:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
612	2026-05-04 23:45:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-05 00:01:00+00	960	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
613	2026-05-05 00:01:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
614	2026-05-05 00:11:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
615	2026-05-05 12:41:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
616	2026-05-05 11:00:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-05 13:56:00+00	10560	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
617	2026-05-05 13:56:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
618	2026-05-05 11:41:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-05 12:25:00+00	2640	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
619	2026-05-05 12:25:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
620	2026-05-05 15:31:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-05 16:56:00+00	5100	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
621	2026-05-05 16:56:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
622	2026-05-05 15:45:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
623	2026-05-05 16:05:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
624	2026-05-05 00:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
625	2026-05-05 00:11:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-05 00:49:00+00	2280	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
626	2026-05-05 00:49:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
627	2026-05-05 02:36:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-05 06:18:00+00	13320	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
628	2026-05-05 06:18:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
629	2026-05-05 05:05:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
630	2026-05-05 07:19:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-05 10:00:00+00	9660	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
631	2026-05-05 10:00:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
632	2026-05-05 09:52:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-05 10:45:00+00	3180	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
633	2026-05-05 10:45:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
634	2026-05-05 12:22:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
635	2026-05-05 14:03:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-05 14:31:00+00	1680	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
636	2026-05-05 14:31:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
637	2026-05-05 15:27:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
638	2026-05-05 02:46:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-05 02:51:00+00	300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
639	2026-05-05 02:51:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
640	2026-05-05 23:13:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-05 23:37:00+00	1440	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
641	2026-05-05 23:37:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
642	2026-05-06 00:18:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
643	2026-05-06 00:09:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
644	2026-05-06 12:53:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-06 16:12:00+00	11940	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
645	2026-05-06 16:12:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
646	2026-05-06 12:00:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-06 13:01:00+00	3660	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
647	2026-05-06 13:01:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
648	2026-05-06 16:31:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-06 17:21:00+00	3000	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
649	2026-05-06 17:21:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
650	2026-05-06 15:40:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-06 17:01:00+00	4860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
651	2026-05-06 17:01:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
652	2026-05-06 16:14:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
653	2026-05-06 01:39:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-06 01:44:00+00	300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
654	2026-05-06 01:44:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
655	2026-05-06 02:34:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-06 06:29:00+00	14100	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
656	2026-05-06 06:29:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
657	2026-05-06 02:39:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-06 05:57:00+00	11880	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
658	2026-05-06 05:57:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
659	2026-05-06 04:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-06 05:10:00+00	2400	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
660	2026-05-06 05:10:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
661	2026-05-06 08:05:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-06 10:06:00+00	7260	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
662	2026-05-06 10:06:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
663	2026-05-06 05:32:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	FORGOT_OFF	\N	2026-05-06 08:12:00+00	9600	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
664	2026-05-06 05:37:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	FORGOT_OFF	\N	2026-05-06 07:44:00+00	7620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
665	2026-05-05 23:59:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-06 00:22:00+00	1380	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
666	2026-05-06 00:22:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
667	2026-05-05 23:36:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-06 00:16:00+00	2400	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
668	2026-05-06 00:16:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
669	2026-05-06 10:12:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-06 11:03:00+00	3060	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
670	2026-05-06 11:03:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
671	2026-05-06 01:16:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-06 01:21:00+00	300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
672	2026-05-06 01:21:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
673	2026-05-07 01:32:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-07 02:08:00+00	2160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
674	2026-05-07 02:08:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
675	2026-05-07 02:32:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-07 02:58:00+00	1560	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
676	2026-05-07 02:58:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
677	2026-05-07 02:30:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-07 08:11:00+00	20460	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
678	2026-05-07 08:11:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
679	2026-05-07 02:40:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
680	2026-05-07 05:00:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-07 05:36:00+00	2160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
681	2026-05-07 05:36:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
682	2026-05-07 12:00:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-07 15:04:00+00	11040	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
683	2026-05-07 15:04:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
684	2026-05-07 15:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-07 15:46:00+00	2760	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
685	2026-05-07 15:46:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
686	2026-05-07 15:10:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
687	2026-05-07 15:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-07 18:58:00+00	14280	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
688	2026-05-07 18:58:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
689	2026-05-07 15:05:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-07 18:42:00+00	13020	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
690	2026-05-07 18:42:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
691	2026-05-07 01:55:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-07 05:24:00+00	12540	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
692	2026-05-07 05:24:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
693	2026-05-07 01:00:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-07 05:54:00+00	17640	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
694	2026-05-07 05:54:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
695	2026-05-07 04:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-07 05:14:00+00	2640	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
696	2026-05-07 05:14:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
697	2026-05-07 07:37:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-07 09:19:00+00	6120	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
698	2026-05-07 09:19:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
699	2026-05-06 23:43:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-07 00:14:00+00	1860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
700	2026-05-07 00:14:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
701	2026-05-07 04:39:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-07 05:13:00+00	2040	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
702	2026-05-07 05:13:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
703	2026-05-07 06:00:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	FORGOT_OFF	\N	2026-05-07 12:01:00+00	21660	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
704	2026-05-07 05:37:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	FORGOT_OFF	\N	2026-05-07 08:46:00+00	11340	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
705	2026-05-07 12:13:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-07 13:55:00+00	6120	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
706	2026-05-07 13:55:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
707	2026-05-07 14:28:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-07 14:57:00+00	1740	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
708	2026-05-07 14:57:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
709	2026-05-07 14:29:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	FORGOT_OFF	\N	2026-05-07 19:43:00+00	18840	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
710	2026-05-08 14:00:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-08 17:04:00+00	11040	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
711	2026-05-08 17:04:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
712	2026-05-08 14:00:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-08 18:43:00+00	16980	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
713	2026-05-08 18:43:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
714	2026-05-07 22:57:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-07 23:34:00+00	2220	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
715	2026-05-07 23:34:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
716	2026-05-08 16:30:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
717	2026-05-07 17:34:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
718	2026-05-07 20:19:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-07 21:47:00+00	5280	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
719	2026-05-07 21:47:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
720	2026-05-08 07:40:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-08 09:40:00+00	7200	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
721	2026-05-08 09:40:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
722	2026-05-08 07:45:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-08 09:56:00+00	7860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
723	2026-05-08 09:56:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
724	2026-05-08 09:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-08 10:08:00+00	2280	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
725	2026-05-08 10:08:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
726	2026-05-09 01:46:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-09 03:03:00+00	4620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
727	2026-05-09 03:03:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
728	2026-05-09 01:15:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-09 02:16:00+00	3660	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
729	2026-05-09 02:16:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
730	2026-05-09 01:15:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-09 01:51:00+00	2160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
731	2026-05-09 01:51:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
732	2026-05-09 13:02:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-09 15:28:00+00	8760	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
733	2026-05-09 15:28:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
734	2026-05-09 11:35:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-09 15:46:00+00	15060	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
735	2026-05-09 15:46:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
736	2026-05-09 12:14:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-09 14:59:00+00	9900	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
737	2026-05-09 14:59:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
738	2026-05-09 16:23:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-09 17:19:00+00	3360	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
739	2026-05-09 17:19:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
740	2026-05-09 16:39:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-09 18:17:00+00	5880	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
741	2026-05-09 18:17:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
742	2026-05-08 23:59:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-09 00:30:00+00	1860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
743	2026-05-09 00:30:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
744	2026-05-09 02:55:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-09 08:38:00+00	20580	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
745	2026-05-09 08:38:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
746	2026-05-09 15:40:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
747	2026-05-10 00:49:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-10 01:35:00+00	2760	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
748	2026-05-10 01:35:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
749	2026-05-10 01:46:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
750	2026-05-10 13:23:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-10 15:42:00+00	8340	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
751	2026-05-10 15:42:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
752	2026-05-10 12:23:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
753	2026-05-10 02:33:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-10 08:27:00+00	21240	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
754	2026-05-10 08:27:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
755	2026-05-10 16:05:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-10 16:32:00+00	1620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
756	2026-05-10 16:32:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
757	2026-05-10 23:02:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-10 23:43:00+00	2460	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
758	2026-05-10 23:43:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
759	2026-05-10 23:26:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-10 23:54:00+00	1680	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
760	2026-05-10 23:54:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
761	2026-05-11 00:08:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
762	2026-05-11 00:20:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
763	2026-05-11 11:09:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-11 14:01:00+00	10320	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
764	2026-05-11 14:01:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
765	2026-05-11 10:31:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-11 13:09:00+00	9480	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
766	2026-05-11 13:09:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
767	2026-05-11 15:29:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-11 16:20:00+00	3060	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
768	2026-05-11 16:20:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
769	2026-05-11 15:39:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-11 17:08:00+00	5340	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
770	2026-05-11 17:08:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
771	2026-05-11 15:54:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
772	2026-05-11 16:08:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
773	2026-05-11 12:38:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-11 14:00:00+00	4920	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
774	2026-05-11 14:00:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
775	2026-05-11 12:09:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-11 12:29:00+00	1200	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
776	2026-05-11 12:29:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
777	2026-05-11 03:14:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-11 06:38:00+00	12240	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
778	2026-05-11 06:38:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
779	2026-05-11 03:19:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-11 07:36:00+00	15420	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
780	2026-05-11 07:36:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
781	2026-05-11 04:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-11 05:12:00+00	2520	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
782	2026-05-11 05:12:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
783	2026-05-11 07:30:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
784	2026-05-11 05:36:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	FORGOT_OFF	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
785	2026-05-11 00:13:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-11 00:49:00+00	2160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
786	2026-05-11 00:49:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
787	2026-05-11 03:26:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-11 03:39:00+00	780	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
788	2026-05-11 03:39:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
789	2026-05-11 04:34:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
790	2026-05-11 10:05:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-11 10:58:00+00	3180	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
791	2026-05-11 10:58:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
792	2026-05-11 14:48:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-11 15:22:00+00	2040	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
793	2026-05-11 15:22:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
794	2026-05-11 14:12:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-11 14:39:00+00	1620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
795	2026-05-11 14:39:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
796	2026-05-11 14:50:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
797	2026-05-11 01:32:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-11 01:37:00+00	300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
798	2026-05-11 01:37:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
799	2026-05-11 22:48:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-11 23:23:00+00	2100	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
800	2026-05-11 23:23:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
801	2026-05-11 23:17:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-11 23:44:00+00	1620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
802	2026-05-11 23:44:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
803	2026-05-12 00:19:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
804	2026-05-12 00:12:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
805	2026-05-12 14:15:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-12 16:44:00+00	8940	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
806	2026-05-12 16:44:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
807	2026-05-12 11:21:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
808	2026-05-12 11:45:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-12 12:30:00+00	2700	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
809	2026-05-12 12:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
810	2026-05-12 15:39:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-12 16:36:00+00	3420	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
811	2026-05-12 16:36:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
812	2026-05-12 15:21:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-12 16:45:00+00	5040	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
813	2026-05-12 16:45:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
814	2026-05-12 16:48:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
815	2026-05-12 02:02:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-12 06:01:00+00	14340	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
816	2026-05-12 06:01:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
817	2026-05-12 02:07:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-12 06:03:00+00	14160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
818	2026-05-12 06:03:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
819	2026-05-12 04:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
820	2026-05-12 07:39:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-12 09:54:00+00	8100	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
821	2026-05-12 09:54:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
822	2026-05-11 23:54:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
823	2026-05-12 03:18:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-12 03:32:00+00	840	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
824	2026-05-12 03:32:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
825	2026-05-12 04:24:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-12 05:12:00+00	2880	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
826	2026-05-12 05:12:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
827	2026-05-12 07:17:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-12 09:55:00+00	9480	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
828	2026-05-12 09:55:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
829	2026-05-12 14:33:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-12 14:58:00+00	1500	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
830	2026-05-12 14:58:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
831	2026-05-12 11:11:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-12 11:16:00+00	300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
832	2026-05-12 11:16:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
833	2026-05-12 22:49:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
834	2026-05-13 11:08:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-13 14:27:00+00	11940	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
835	2026-05-13 14:27:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
836	2026-05-13 15:06:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
837	2026-05-13 10:37:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-13 10:42:00+00	300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
838	2026-05-13 10:42:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
839	2026-05-13 23:14:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-13 23:51:00+00	2220	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
840	2026-05-13 23:51:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
841	2026-05-13 23:24:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-13 23:48:00+00	1440	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
842	2026-05-13 23:48:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
843	2026-05-14 00:36:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
844	2026-05-14 10:55:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-14 13:21:00+00	8760	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
845	2026-05-14 13:21:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
846	2026-05-14 12:09:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
847	2026-05-14 13:06:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-14 14:55:00+00	6540	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
848	2026-05-14 14:55:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
849	2026-05-14 16:26:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-14 17:09:00+00	2580	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
850	2026-05-14 17:09:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
851	2026-05-14 15:38:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-14 17:04:00+00	5160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
852	2026-05-14 17:04:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
853	2026-05-14 15:45:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
854	2026-05-14 16:04:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
855	2026-05-14 01:33:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-14 04:45:00+00	11520	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
856	2026-05-14 04:45:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
857	2026-05-14 04:06:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
858	2026-05-14 04:22:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-14 05:08:00+00	2760	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
859	2026-05-14 05:08:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
860	2026-05-14 06:04:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-14 07:07:00+00	3780	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
861	2026-05-14 07:07:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
862	2026-05-14 06:52:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-14 09:18:00+00	8760	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
863	2026-05-14 09:18:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
864	2026-05-14 07:59:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-14 10:04:00+00	7500	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
865	2026-05-14 10:04:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
866	2026-05-14 07:37:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
867	2026-05-14 14:22:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-14 14:53:00+00	1860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
868	2026-05-14 14:53:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
869	2026-05-14 11:36:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-14 12:21:00+00	2700	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
870	2026-05-14 12:21:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
871	2026-05-14 11:54:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-14 12:20:00+00	1560	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
872	2026-05-14 12:20:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
873	2026-05-14 22:39:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-14 23:27:00+00	2880	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
874	2026-05-14 23:27:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
875	2026-05-14 22:47:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-14 23:32:00+00	2700	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
876	2026-05-14 23:32:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
877	2026-05-14 23:24:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-14 23:38:00+00	840	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
878	2026-05-14 23:38:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
879	2026-05-15 00:24:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
880	2026-05-15 00:14:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
881	2026-05-15 10:34:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
882	2026-05-15 14:59:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-15 15:50:00+00	3060	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
883	2026-05-15 15:50:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
884	2026-05-15 15:59:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-15 17:25:00+00	5160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
885	2026-05-15 17:25:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
886	2026-05-15 16:24:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
887	2026-05-15 02:02:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-15 06:40:00+00	16680	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
888	2026-05-15 06:40:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
889	2026-05-15 02:07:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-15 05:27:00+00	12000	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
890	2026-05-15 05:27:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
891	2026-05-15 04:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-15 05:03:00+00	1980	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
892	2026-05-15 05:03:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
893	2026-05-15 07:30:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-15 10:19:00+00	10140	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
894	2026-05-15 10:19:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
895	2026-05-14 23:51:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
896	2026-05-15 00:22:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-15 00:59:00+00	2220	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
897	2026-05-15 00:59:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
898	2026-05-15 03:26:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
899	2026-05-15 04:27:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-15 05:20:00+00	3180	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
900	2026-05-15 05:20:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
901	2026-05-15 10:04:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-15 10:58:00+00	3240	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
902	2026-05-15 10:58:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
903	2026-05-15 14:50:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
904	2026-05-16 00:01:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
905	2026-05-16 02:42:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-16 04:29:00+00	6420	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
906	2026-05-16 04:29:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
907	2026-05-16 11:55:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-16 14:20:00+00	8700	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
908	2026-05-16 14:20:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
909	2026-05-17 00:54:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-17 01:51:00+00	3420	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
910	2026-05-17 01:51:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
911	2026-05-17 01:10:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-17 01:47:00+00	2220	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
912	2026-05-17 01:47:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
913	2026-05-17 12:19:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-17 13:57:00+00	5880	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
914	2026-05-17 13:57:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
915	2026-05-17 11:49:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-17 15:21:00+00	12720	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
916	2026-05-17 15:21:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
917	2026-05-17 12:09:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-17 15:10:00+00	10860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
918	2026-05-17 15:10:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
919	2026-05-17 16:41:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-17 17:43:00+00	3720	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
920	2026-05-17 17:43:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
921	2026-05-16 23:33:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
922	2026-05-17 01:38:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-17 02:24:00+00	2760	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
923	2026-05-17 02:24:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
924	2026-05-17 02:15:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-17 07:46:00+00	19860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
925	2026-05-17 07:46:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
926	2026-05-17 02:46:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-17 07:32:00+00	17160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
927	2026-05-17 07:32:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
928	2026-05-17 07:37:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-17 09:10:00+00	5580	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
929	2026-05-17 09:10:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
930	2026-05-17 15:15:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
931	2026-05-18 14:00:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-18 21:03:00+00	25380	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
932	2026-05-18 21:03:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
933	2026-05-18 14:00:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-18 19:41:00+00	20460	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
934	2026-05-18 19:41:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
935	2026-05-17 23:01:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-17 23:50:00+00	2940	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
936	2026-05-17 23:50:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
937	2026-05-17 22:55:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-17 23:38:00+00	2580	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
938	2026-05-17 23:38:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
939	2026-05-17 23:33:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-18 00:01:00+00	1680	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
940	2026-05-18 00:01:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
941	2026-05-18 00:15:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
942	2026-05-18 11:42:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-18 12:16:00+00	2040	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
943	2026-05-18 12:16:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
944	2026-05-18 15:40:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-18 16:27:00+00	2820	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
945	2026-05-18 16:27:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
946	2026-05-18 15:47:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
947	2026-05-18 16:20:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
948	2026-05-18 12:20:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-18 13:12:00+00	3120	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
949	2026-05-18 13:12:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
950	2026-05-18 12:28:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-18 13:05:00+00	2220	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
951	2026-05-18 13:05:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
952	2026-05-17 23:55:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-18 00:35:00+00	2400	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
953	2026-05-18 00:35:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
954	2026-05-18 01:52:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
955	2026-05-18 02:05:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-18 05:54:00+00	13740	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
956	2026-05-18 05:54:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
957	2026-05-18 04:36:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-18 05:14:00+00	2280	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
958	2026-05-18 05:14:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
959	2026-05-18 06:10:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-18 07:20:00+00	4200	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
960	2026-05-18 07:20:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
961	2026-05-18 06:07:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-18 07:11:00+00	3840	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
962	2026-05-18 07:11:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
963	2026-05-18 07:22:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-18 09:33:00+00	7860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
964	2026-05-18 09:33:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
965	2026-05-18 07:30:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-18 10:19:00+00	10140	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
966	2026-05-18 10:19:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
967	2026-05-18 07:23:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-18 09:51:00+00	8880	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
968	2026-05-18 09:51:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
969	2026-05-18 14:40:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
970	2026-05-18 12:07:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
971	2026-05-18 12:53:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-18 13:22:00+00	1740	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
972	2026-05-18 13:22:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
973	2026-05-18 22:54:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-18 23:30:00+00	2160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
974	2026-05-18 23:30:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
975	2026-05-18 23:09:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-18 23:43:00+00	2040	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
976	2026-05-18 23:43:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
977	2026-05-18 23:25:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-18 23:52:00+00	1620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
978	2026-05-18 23:52:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
979	2026-05-19 00:15:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
980	2026-05-19 00:22:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
981	2026-05-19 10:51:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-19 13:26:00+00	9300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
982	2026-05-19 13:26:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
983	2026-05-19 13:13:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
984	2026-05-19 11:36:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
985	2026-05-19 15:27:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-19 16:26:00+00	3540	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
986	2026-05-19 16:26:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
987	2026-05-19 15:38:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-19 16:47:00+00	4140	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
988	2026-05-19 16:47:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
989	2026-05-19 15:52:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
990	2026-05-19 16:07:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
991	2026-05-18 23:55:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-19 00:31:00+00	2160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
992	2026-05-19 00:31:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
993	2026-05-19 01:49:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
994	2026-05-19 02:21:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-19 06:04:00+00	13380	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
995	2026-05-19 06:04:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
996	2026-05-19 04:33:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
997	2026-05-19 06:12:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-19 07:13:00+00	3660	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
998	2026-05-19 07:13:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
999	2026-05-19 07:06:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-19 09:13:00+00	7620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1000	2026-05-19 09:13:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1001	2026-05-19 07:25:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-19 09:30:00+00	7500	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1002	2026-05-19 09:30:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1003	2026-05-19 06:52:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-19 09:33:00+00	9660	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1004	2026-05-19 09:33:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1005	2026-05-19 12:16:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-19 13:35:00+00	4740	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1006	2026-05-19 13:35:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1007	2026-05-19 14:32:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1008	2026-05-19 14:40:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-19 15:06:00+00	1560	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1009	2026-05-19 15:06:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1010	2026-05-19 15:10:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1011	2026-05-19 23:10:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-19 23:39:00+00	1740	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1012	2026-05-19 23:39:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1013	2026-05-19 23:28:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-19 23:58:00+00	1800	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1014	2026-05-19 23:58:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1015	2026-05-20 00:09:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1016	2026-05-20 00:17:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1017	2026-05-20 11:11:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-20 15:02:00+00	13860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1018	2026-05-20 15:02:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1019	2026-05-20 11:24:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1020	2026-05-20 15:16:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-20 17:29:00+00	7980	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1021	2026-05-20 17:29:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1022	2026-05-20 16:24:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-20 17:47:00+00	4980	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1023	2026-05-20 17:47:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1024	2026-05-19 23:38:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-20 00:14:00+00	2160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1025	2026-05-20 00:14:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1026	2026-05-20 00:01:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-20 00:41:00+00	2400	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1027	2026-05-20 00:41:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1028	2026-05-20 02:02:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-20 06:07:00+00	14700	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1029	2026-05-20 06:07:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1030	2026-05-20 03:46:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-20 03:59:00+00	780	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1031	2026-05-20 03:59:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1032	2026-05-20 04:18:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-20 04:52:00+00	2040	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1033	2026-05-20 04:52:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1034	2026-05-20 07:10:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1035	2026-05-20 07:24:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-20 09:11:00+00	6420	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1036	2026-05-20 09:11:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1037	2026-05-20 09:58:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-20 10:52:00+00	3240	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1038	2026-05-20 10:52:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1039	2026-05-20 12:16:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-20 14:12:00+00	6960	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1040	2026-05-20 14:12:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1041	2026-05-20 14:36:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1042	2026-05-20 15:11:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1043	2026-05-20 06:05:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1044	2026-05-21 02:25:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-21 03:22:00+00	3420	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1045	2026-05-21 03:22:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1046	2026-05-21 03:25:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-21 03:56:00+00	1860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1047	2026-05-21 03:56:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1048	2026-05-21 02:30:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1049	2026-05-21 02:40:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-21 07:18:00+00	16680	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1050	2026-05-21 07:18:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1051	2026-05-21 05:00:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-21 05:37:00+00	2220	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1052	2026-05-21 05:37:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1053	2026-05-21 12:00:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-21 14:54:00+00	10440	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1054	2026-05-21 14:54:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1055	2026-05-21 15:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-21 15:35:00+00	2100	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1056	2026-05-21 15:35:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1057	2026-05-21 15:10:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-21 16:27:00+00	4620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1058	2026-05-21 16:27:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1059	2026-05-21 15:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-21 18:36:00+00	12960	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1060	2026-05-21 18:36:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1061	2026-05-21 15:05:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-21 17:52:00+00	10020	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1062	2026-05-21 17:52:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1063	2026-05-21 06:14:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-21 07:23:00+00	4140	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1064	2026-05-21 07:23:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1065	2026-05-21 06:39:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-21 07:38:00+00	3540	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1066	2026-05-21 07:38:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1067	2026-05-21 06:43:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-21 08:38:00+00	6900	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1068	2026-05-21 08:38:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1069	2026-05-21 07:27:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-21 09:18:00+00	6660	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1070	2026-05-21 09:18:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1071	2026-05-21 08:02:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-21 10:16:00+00	8040	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1072	2026-05-21 10:16:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1073	2026-05-21 10:09:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-21 11:08:00+00	3540	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1074	2026-05-21 11:08:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1075	2026-05-21 13:49:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-21 14:19:00+00	1800	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1076	2026-05-21 14:19:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1077	2026-05-21 20:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-21 20:50:00+00	3000	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1078	2026-05-21 20:50:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1079	2026-05-21 23:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-21 23:45:00+00	2700	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1080	2026-05-21 23:45:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1081	2026-05-21 23:12:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-21 23:55:00+00	2580	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1082	2026-05-21 23:55:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1083	2026-05-21 23:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-21 23:57:00+00	1620	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1084	2026-05-21 23:57:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1085	2026-05-22 00:19:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1086	2026-05-22 00:29:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1087	2026-05-22 10:57:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-22 14:03:00+00	11160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1088	2026-05-22 14:03:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1089	2026-05-22 12:09:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-22 12:47:00+00	2280	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1090	2026-05-22 12:47:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1091	2026-05-22 15:37:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1092	2026-05-22 15:51:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-22 17:36:00+00	6300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1093	2026-05-22 17:36:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1094	2026-05-22 15:48:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1095	2026-05-22 16:05:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1096	2026-05-22 08:53:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-22 08:58:00+00	300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1097	2026-05-22 08:58:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1098	2026-05-22 07:48:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-22 09:37:00+00	6540	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1099	2026-05-22 09:37:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1100	2026-05-22 07:53:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-22 09:26:00+00	5580	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1101	2026-05-22 09:26:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1102	2026-05-22 09:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1103	2026-05-23 12:47:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-23 14:36:00+00	6540	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1104	2026-05-23 14:36:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1105	2026-05-23 11:33:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-23 15:35:00+00	14520	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1106	2026-05-23 15:35:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1107	2026-05-23 16:41:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-23 17:37:00+00	3360	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1108	2026-05-23 17:37:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1109	2026-05-23 16:44:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-23 18:35:00+00	6660	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1110	2026-05-23 18:35:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1111	2026-05-22 23:38:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1112	2026-05-23 02:44:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-23 08:44:00+00	21600	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1113	2026-05-23 08:44:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1114	2026-05-23 06:13:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-23 08:34:00+00	8460	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1115	2026-05-23 08:34:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1116	2026-05-23 15:25:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-23 15:54:00+00	1740	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1117	2026-05-23 15:54:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1118	2026-05-24 01:00:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-24 01:42:00+00	2520	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1119	2026-05-24 01:42:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1120	2026-05-24 12:36:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-24 14:36:00+00	7200	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1121	2026-05-24 14:36:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1122	2026-05-24 12:31:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1123	2026-05-24 16:50:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-24 18:16:00+00	5160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1124	2026-05-24 18:16:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1125	2026-05-23 23:19:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1126	2026-05-24 03:13:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1127	2026-05-24 02:55:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-24 08:15:00+00	19200	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1128	2026-05-24 08:15:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1129	2026-05-24 15:30:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1130	2026-05-24 15:56:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-24 17:16:00+00	4800	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1131	2026-05-24 17:16:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1132	2026-05-24 23:00:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-24 23:38:00+00	2280	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1133	2026-05-24 23:38:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1134	2026-05-24 23:06:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-24 23:27:00+00	1260	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1135	2026-05-24 23:27:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1136	2026-05-25 00:15:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1137	2026-05-25 00:27:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1138	2026-05-25 13:58:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-25 16:34:00+00	9360	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1139	2026-05-25 16:34:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1140	2026-05-25 11:53:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1141	2026-05-25 15:22:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-25 16:09:00+00	2820	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1142	2026-05-25 16:09:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1143	2026-05-25 15:47:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1144	2026-05-25 16:01:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1145	2026-05-24 20:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-24 20:41:00+00	2460	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1146	2026-05-24 20:41:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1147	2026-05-24 20:15:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-24 20:33:00+00	1080	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1148	2026-05-24 20:33:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1149	2026-05-24 23:35:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-25 00:09:00+00	2040	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1150	2026-05-25 00:09:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1151	2026-05-24 23:43:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1152	2026-05-25 01:55:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-25 04:55:00+00	10800	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1153	2026-05-25 04:55:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1154	2026-05-25 04:38:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-25 05:16:00+00	2280	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1155	2026-05-25 05:16:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1156	2026-05-25 06:36:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-25 08:05:00+00	5340	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1157	2026-05-25 08:05:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1158	2026-05-25 07:26:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-25 09:41:00+00	8100	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1159	2026-05-25 09:41:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1160	2026-05-25 08:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-25 10:26:00+00	8760	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1161	2026-05-25 10:26:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1162	2026-05-25 07:28:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-25 09:57:00+00	8940	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1163	2026-05-25 09:57:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1164	2026-05-25 10:01:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-25 10:55:00+00	3240	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1165	2026-05-25 10:55:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1166	2026-05-25 14:17:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-25 14:50:00+00	1980	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1167	2026-05-25 14:50:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1168	2026-05-25 14:38:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-25 15:07:00+00	1740	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1169	2026-05-25 15:07:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1170	2026-05-25 22:52:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-25 23:46:00+00	3240	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1171	2026-05-25 23:46:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1172	2026-05-25 23:15:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-25 23:50:00+00	2100	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1173	2026-05-25 23:50:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1174	2026-05-26 00:10:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1175	2026-05-26 11:42:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-26 12:21:00+00	2340	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1176	2026-05-26 12:21:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1177	2026-05-26 15:17:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-26 16:13:00+00	3360	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1178	2026-05-26 16:13:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1179	2026-05-26 16:35:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-26 17:59:00+00	5040	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1180	2026-05-26 17:59:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1181	2026-05-26 16:03:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1182	2026-05-26 16:05:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1183	2026-05-26 14:17:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-26 14:22:00+00	300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1184	2026-05-26 14:22:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1185	2026-05-26 02:13:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-26 05:30:00+00	11820	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1186	2026-05-26 05:30:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1187	2026-05-26 02:18:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-26 05:48:00+00	12600	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1188	2026-05-26 05:48:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1189	2026-05-26 04:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-26 05:06:00+00	2160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1190	2026-05-26 05:06:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1191	2026-05-26 07:55:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-26 10:53:00+00	10680	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1192	2026-05-26 10:53:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1193	2026-05-25 23:44:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-26 00:26:00+00	2520	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1194	2026-05-26 00:26:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1195	2026-05-26 03:51:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-26 04:39:00+00	2880	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1196	2026-05-26 04:39:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1197	2026-05-26 09:57:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-26 11:07:00+00	4200	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1198	2026-05-26 11:07:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1199	2026-05-26 12:38:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-26 14:07:00+00	5340	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1200	2026-05-26 14:07:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1201	2026-05-26 23:16:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-26 23:58:00+00	2520	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1202	2026-05-26 23:58:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1203	2026-05-26 23:03:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-26 23:45:00+00	2520	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1204	2026-05-26 23:45:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1205	2026-05-27 00:23:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1206	2026-05-27 00:27:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1207	2026-05-27 10:28:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-27 13:45:00+00	11820	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1208	2026-05-27 13:45:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1209	2026-05-27 11:05:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-27 14:30:00+00	12300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1210	2026-05-27 14:30:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1211	2026-05-27 15:12:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-27 16:13:00+00	3660	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1212	2026-05-27 16:13:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1213	2026-05-27 15:02:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-27 17:01:00+00	7140	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1214	2026-05-27 17:01:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1215	2026-05-27 15:27:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-27 17:11:00+00	6240	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1216	2026-05-27 17:11:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1217	2026-05-27 15:55:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1218	2026-05-27 16:05:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1219	2026-05-27 15:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-27 20:15:00+00	18900	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1220	2026-05-27 20:15:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1221	2026-05-27 15:05:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-27 20:38:00+00	19980	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1222	2026-05-27 20:38:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1223	2026-05-26 23:39:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-27 00:21:00+00	2520	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1224	2026-05-27 00:21:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1225	2026-05-27 02:33:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-27 06:23:00+00	13800	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1226	2026-05-27 06:23:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1227	2026-05-27 04:00:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-27 04:16:00+00	960	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1228	2026-05-27 04:16:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1229	2026-05-27 04:43:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-27 05:29:00+00	2760	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1230	2026-05-27 05:29:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1231	2026-05-27 08:52:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-27 10:55:00+00	7380	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1232	2026-05-27 10:55:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1233	2026-05-27 14:26:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-27 14:47:00+00	1260	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1234	2026-05-27 14:47:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1235	2026-05-27 15:20:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1236	2026-05-28 00:06:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1237	2026-05-28 12:08:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-28 13:01:00+00	3180	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1238	2026-05-28 13:01:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1239	2026-05-28 13:07:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-28 14:55:00+00	6480	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1240	2026-05-28 14:55:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1241	2026-05-28 15:26:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-28 16:12:00+00	2760	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1242	2026-05-28 16:12:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1243	2026-05-28 15:23:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-28 16:30:00+00	4020	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1244	2026-05-28 16:30:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1245	2026-05-28 16:08:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1246	2026-05-28 16:27:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1247	2026-05-28 03:19:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-28 03:36:00+00	1020	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1248	2026-05-28 03:36:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1249	2026-05-28 04:22:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1250	2026-05-28 05:51:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-28 07:16:00+00	5100	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1251	2026-05-28 07:16:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1252	2026-05-28 07:00:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-28 08:52:00+00	6720	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1253	2026-05-28 08:52:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1254	2026-05-28 08:03:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1255	2026-05-28 07:56:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-28 10:24:00+00	8880	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1256	2026-05-28 10:24:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1257	2026-05-28 10:10:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-28 11:18:00+00	4080	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1258	2026-05-28 11:18:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1259	2026-05-28 12:17:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-28 13:47:00+00	5400	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1260	2026-05-28 13:47:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1261	2026-05-28 14:35:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1262	2026-05-28 15:06:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1263	2026-05-29 14:00:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-29 17:12:00+00	11520	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1264	2026-05-29 17:12:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1265	2026-05-29 14:00:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-29 17:30:00+00	12600	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1266	2026-05-29 17:30:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1267	2026-05-28 23:02:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-28 23:39:00+00	2220	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1268	2026-05-28 23:39:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1269	2026-05-28 23:22:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-28 23:45:00+00	1380	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1270	2026-05-28 23:45:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1271	2026-05-29 00:40:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1272	2026-05-29 11:01:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-29 13:33:00+00	9120	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1273	2026-05-29 13:33:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1274	2026-05-29 11:12:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-29 13:28:00+00	8160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1275	2026-05-29 13:28:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1276	2026-05-29 15:52:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1277	2026-05-29 15:40:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-29 17:17:00+00	5820	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1278	2026-05-29 17:17:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1279	2026-05-29 15:58:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1280	2026-05-29 16:51:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1281	2026-05-29 13:23:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-29 14:37:00+00	4440	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1282	2026-05-29 14:37:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1283	2026-05-29 13:56:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-29 14:44:00+00	2880	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1284	2026-05-29 14:44:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1285	2026-05-29 02:08:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-29 06:51:00+00	16980	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1286	2026-05-29 06:51:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1287	2026-05-29 02:13:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-29 06:19:00+00	14760	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1288	2026-05-29 06:19:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1289	2026-05-29 04:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-29 05:18:00+00	2880	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1290	2026-05-29 05:18:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1291	2026-05-29 07:50:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-29 10:28:00+00	9480	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1292	2026-05-29 10:28:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1293	2026-05-29 04:03:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-29 04:46:00+00	2580	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1294	2026-05-29 04:46:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1295	2026-05-29 05:25:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1296	2026-05-29 12:43:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1297	2026-05-29 14:18:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-29 14:49:00+00	1860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1298	2026-05-29 14:49:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1299	2026-05-29 14:53:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1300	2026-05-29 09:35:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-29 09:40:00+00	300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1301	2026-05-29 09:40:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1302	2026-05-30 14:00:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-30 19:34:00+00	20040	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1303	2026-05-30 19:34:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1304	2026-05-30 14:00:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-30 20:28:00+00	23280	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1305	2026-05-30 20:28:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1306	2026-05-29 20:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-29 20:54:00+00	3240	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1307	2026-05-29 20:54:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1308	2026-05-29 20:15:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-29 20:28:00+00	780	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1309	2026-05-29 20:28:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1310	2026-05-30 01:25:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-30 02:15:00+00	3000	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1311	2026-05-30 02:15:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1312	2026-05-30 13:21:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-30 15:09:00+00	6480	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1313	2026-05-30 15:09:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1314	2026-05-30 11:29:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-30 15:33:00+00	14640	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1315	2026-05-30 15:33:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1316	2026-05-30 16:46:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-30 18:07:00+00	4860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1317	2026-05-30 18:07:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1318	2026-05-30 01:47:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-30 02:45:00+00	3480	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1319	2026-05-30 02:45:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1320	2026-05-30 02:45:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-30 07:50:00+00	18300	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1321	2026-05-30 07:50:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1322	2026-05-30 15:26:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-30 15:56:00+00	1800	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1323	2026-05-30 15:56:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1324	2026-05-30 15:19:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-30 16:35:00+00	4560	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1325	2026-05-30 16:35:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1326	2026-05-31 14:00:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-31 18:55:00+00	17700	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1327	2026-05-31 18:55:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1328	2026-05-31 14:00:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-31 18:33:00+00	16380	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1329	2026-05-31 18:33:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1330	2026-05-31 16:43:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-31 17:56:00+00	4380	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1331	2026-05-31 17:56:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1332	2026-05-31 16:05:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-31 17:41:00+00	5760	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1333	2026-05-31 17:41:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1334	2026-05-30 22:45:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-31 00:24:00+00	5940	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1335	2026-05-31 00:24:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1336	2026-05-30 18:09:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-05-30 20:41:00+00	9120	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1337	2026-05-30 20:41:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1338	2026-05-31 05:46:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	FORGOT_OFF	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1339	2026-05-30 21:15:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-30 22:57:00+00	6120	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1340	2026-05-30 22:57:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1341	2026-05-30 20:04:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-05-30 21:10:00+00	3960	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1342	2026-05-30 21:10:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	PHYSICAL_UNKNOWN	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1343	2026-06-02 00:00:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	\N	DEVICE_ON	\N	2026-06-02 00:18:00+00	1080	SCHEDULE	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1344	2026-06-02 00:18:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	\N	DEVICE_OFF	\N	\N	0	SCHEDULE	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1345	2026-06-03 00:00:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	\N	DEVICE_ON	\N	2026-06-03 00:16:00+00	960	SCHEDULE	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1346	2026-06-03 00:16:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	\N	DEVICE_OFF	\N	\N	0	SCHEDULE	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1347	2026-06-03 21:00:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-06-03 21:20:00+00	1200	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1348	2026-06-03 21:20:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1349	2026-06-05 14:00:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-06-05 18:44:00+00	17040	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1350	2026-06-05 18:44:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1351	2026-06-05 14:00:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-06-05 19:31:00+00	19860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1352	2026-06-05 19:31:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1353	2026-06-04 23:20:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-06-04 23:59:00+00	2340	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1354	2026-06-04 23:59:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1355	2026-06-04 23:33:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1356	2026-06-05 00:05:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1357	2026-06-05 11:01:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-06-05 13:35:00+00	9240	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1358	2026-06-05 13:35:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1359	2026-06-05 11:18:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-06-05 14:20:00+00	10920	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1360	2026-06-05 14:20:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1361	2026-06-05 12:16:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-06-05 13:10:00+00	3240	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1362	2026-06-05 13:10:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1363	2026-06-05 15:48:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-06-05 16:30:00+00	2520	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1364	2026-06-05 16:30:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1365	2026-06-05 16:01:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1366	2026-06-05 16:50:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1367	2026-06-05 02:19:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-06-05 06:28:00+00	14940	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1368	2026-06-05 06:28:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1369	2026-06-05 02:24:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-06-05 05:45:00+00	12060	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1370	2026-06-05 05:45:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1371	2026-06-05 04:30:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1372	2026-06-05 07:03:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-06-05 08:57:00+00	6840	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1373	2026-06-05 08:57:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1374	2026-06-04 23:34:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-06-05 00:10:00+00	2160	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1375	2026-06-05 00:10:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1376	2026-06-04 23:47:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-06-05 00:33:00+00	2760	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1377	2026-06-05 00:33:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1378	2026-06-05 03:40:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-06-05 03:59:00+00	1140	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1379	2026-06-05 03:59:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1380	2026-06-05 04:29:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-06-05 05:20:00+00	3060	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1381	2026-06-05 05:20:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1382	2026-06-05 06:20:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1383	2026-06-05 06:26:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-06-05 07:35:00+00	4140	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1384	2026-06-05 07:35:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1385	2026-06-05 07:41:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-06-05 09:32:00+00	6660	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1386	2026-06-05 09:32:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1387	2026-06-05 10:08:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-06-05 11:13:00+00	3900	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1388	2026-06-05 11:13:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1389	2026-06-05 11:49:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-06-05 13:50:00+00	7260	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1390	2026-06-05 13:50:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1391	2026-06-05 15:03:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-06-05 15:40:00+00	2220	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1392	2026-06-05 15:40:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1393	2026-06-05 14:34:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-06-05 14:57:00+00	1380	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1394	2026-06-05 14:57:00+00	2df56b5d-2a60-4382-bda8-e150df7805e1	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1395	2026-06-05 14:54:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1396	2026-06-06 01:34:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-06-06 02:19:00+00	2700	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1397	2026-06-06 02:19:00+00	af1dad60-6dbd-4093-88c4-d041f3515c17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1398	2026-06-06 01:32:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-06-06 03:24:00+00	6720	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1399	2026-06-06 03:24:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1400	2026-06-06 13:07:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-06-06 15:11:00+00	7440	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1401	2026-06-06 15:11:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1402	2026-06-06 11:28:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	\N	\N	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1403	2026-06-06 12:27:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-06-06 15:12:00+00	9900	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1404	2026-06-06 15:12:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1405	2026-06-06 16:39:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-06-06 18:02:00+00	4980	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1406	2026-06-06 18:02:00+00	b29217ff-2b22-4cdb-a25e-828ba5011266	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1407	2026-06-06 01:52:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-06-06 07:35:00+00	20580	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1408	2026-06-06 07:35:00+00	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1409	2026-06-06 02:44:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-06-06 07:48:00+00	18240	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1410	2026-06-06 07:48:00+00	ef359599-bea0-4f11-8de4-f6c433fbc7fb	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1411	2026-06-06 06:56:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-06-06 09:01:00+00	7500	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1412	2026-06-06 09:01:00+00	6cb5a041-7821-4ca8-8c2c-15363bc35047	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1413	2026-06-06 15:14:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_ON	\N	2026-06-06 15:45:00+00	1860	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1414	2026-06-06 15:45:00+00	aacca680-7fa2-41e3-996b-c15a56718f9d	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	DEVICE_OFF	\N	\N	0	USER	\N	3716450c-0d6b-4900-9341-b68b64b44bed
1415	2026-06-08 04:27:40.085085+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_ON	\N	2026-06-08 04:27:40.677143+00	0	USER	{"source": "device_state_transition"}	3716450c-0d6b-4900-9341-b68b64b44bed
1416	2026-06-08 04:27:40.677143+00	aacca680-7fa2-41e3-996b-c15a56718f9d	910adcc3-fd19-48e5-8cdc-13e16cf212f7	DEVICE_OFF	\N	2026-06-08 04:27:40.677143+00	0	USER	{"source": "device_state_transition"}	3716450c-0d6b-4900-9341-b68b64b44bed
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
f1a2b3c4d5e6
\.


--
-- Data for Name: auth_sessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_sessions (id, user_id, refresh_token_hash, user_agent, ip_address, created_at, expires_at, last_used_at, revoked_at) FROM stdin;
39daab1d-ac9f-47dc-8cd2-9eea0e2e3b9d	730f5d00-bec1-464e-b794-6d3c9fe75e26	20e6438ef4c837ef63290cf76ed2b8d56875e50d676f6a28a1e5735c2821cdcb	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0	172.18.0.1	2026-06-07 07:15:55.868165+00	2026-06-14 07:15:55.867188+00	\N	\N
911bdb7b-0ea3-461d-a548-483c36a92a2d	730f5d00-bec1-464e-b794-6d3c9fe75e26	373d2e9701e16ff176f70dffc32efccaa6aafa93633d2ea92b7bedae4024b326	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0	172.18.0.1	2026-06-07 07:20:06.692044+00	2026-06-14 07:20:06.691578+00	\N	\N
d8941a28-c941-4763-8a1d-95726f5f4dce	910adcc3-fd19-48e5-8cdc-13e16cf212f7	1681d633850eafeec214cccafe38019fa9c9e337aa0587256b27305ba62360b0	Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.26100.8457	172.18.0.1	2026-06-07 07:23:37.721975+00	2026-06-14 07:23:37.72146+00	\N	\N
88fe6b02-22e3-4c7f-857b-6a4e59a03217	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0f599b8cca0bc0491aca58fcf9cf177afacfcf919b0e7583e214d40c1b949471	Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.26100.8457	172.18.0.1	2026-06-07 07:23:37.979229+00	2026-06-14 07:23:37.978805+00	\N	\N
c0eef79e-fa6c-4e32-98ae-8feeda9832a6	910adcc3-fd19-48e5-8cdc-13e16cf212f7	03c0d4a374a7a90d5fbb24f5c566b0b79f63f19a7761a3a7a8aa3e35b296a558	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0	172.18.0.1	2026-06-07 07:24:02.439233+00	2026-06-14 07:54:07.984436+00	2026-06-07 07:54:07.984441+00	\N
9725ef1f-498b-40dc-846e-ca5847998229	910adcc3-fd19-48e5-8cdc-13e16cf212f7	cc43f14fda50b0313bd1e0d19387e0af106480ed23edd44a60a77907b412df5b	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36	172.18.0.1	2026-06-08 04:27:22.243453+00	2026-06-15 04:27:22.241672+00	\N	\N
\.


--
-- Data for Name: automation_actions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.automation_actions (id, automation_id, device_id, action, value) FROM stdin;
\.


--
-- Data for Name: automation_conditions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.automation_conditions (id, automation_id, condition_type, value) FROM stdin;
\.


--
-- Data for Name: automations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.automations (id, home_id, name, enabled, created_at) FROM stdin;
\.


--
-- Data for Name: device_logs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.device_logs (id, device_id, action, value, "timestamp") FROM stdin;
0600bb04-765e-4ef6-8197-7c613a5ffee3	ef359599-bea0-4f11-8de4-f6c433fbc7fb	turn_off	None	2026-06-07 07:30:45.399419
72a1e2d3-24de-4bb0-aebd-c8b7a7be551c	aacca680-7fa2-41e3-996b-c15a56718f9d	toggle	True	2026-06-08 04:27:40.095814
9239ccec-5571-4257-87a8-a6b23636a17c	aacca680-7fa2-41e3-996b-c15a56718f9d	toggle	False	2026-06-08 04:27:40.691129
\.


--
-- Data for Name: device_states; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.device_states (device_id, is_online, state, last_updated) FROM stdin;
2df56b5d-2a60-4382-bda8-e150df7805e1	t	{"power": "OFF"}	2026-06-07 06:58:43.647579+00
b29217ff-2b22-4cdb-a25e-828ba5011266	t	{"power": "OFF"}	2026-06-07 06:58:43.647579+00
5c3941b6-cf40-4842-bbbc-2d36bbbdee25	t	{"power": "OFF"}	2026-06-07 06:58:43.647579+00
6cb5a041-7821-4ca8-8c2c-15363bc35047	t	{"power": "OFF"}	2026-06-07 06:58:43.647579+00
af1dad60-6dbd-4093-88c4-d041f3515c17	t	{"power": "OFF"}	2026-06-07 06:58:43.647579+00
bc48d66a-a277-4b69-979d-897203380a40	t	{}	2026-06-07 06:58:43.647579+00
c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	t	{}	2026-06-07 06:58:43.647579+00
ef359599-bea0-4f11-8de4-f6c433fbc7fb	t	{"power": "OFF"}	2026-06-07 07:30:45.395956+00
aacca680-7fa2-41e3-996b-c15a56718f9d	t	{"power": "OFF"}	2026-06-08 04:27:40.676422+00
\.


--
-- Data for Name: devices; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.devices (id, slug, room_id, name, type, mqtt_topic, config, created_at) FROM stdin;
aacca680-7fa2-41e3-996b-c15a56718f9d	light_bedroom	3fea41ca-7383-4768-9a45-80704d5bbb69	Đèn phòng ngủ	LIGHT	home/light_bedroom	{}	2026-06-07 06:58:43.647579+00
2df56b5d-2a60-4382-bda8-e150df7805e1	fan_bedroom	3fea41ca-7383-4768-9a45-80704d5bbb69	Quạt phòng ngủ	FAN	home/fan_bedroom	{}	2026-06-07 06:58:43.647579+00
b29217ff-2b22-4cdb-a25e-828ba5011266	ac_bedroom	3fea41ca-7383-4768-9a45-80704d5bbb69	Điều hoà phòng ngủ	AC	home/ac_bedroom	{}	2026-06-07 06:58:43.647579+00
5c3941b6-cf40-4842-bbbc-2d36bbbdee25	light_living	5924d74e-e6e3-4497-afe8-69712c5e4a7a	Đèn phòng khách	LIGHT	home/light_living	{}	2026-06-07 06:58:43.647579+00
ef359599-bea0-4f11-8de4-f6c433fbc7fb	fan_living	5924d74e-e6e3-4497-afe8-69712c5e4a7a	Quạt phòng khách	FAN	home/fan_living	{}	2026-06-07 06:58:43.647579+00
6cb5a041-7821-4ca8-8c2c-15363bc35047	ac_living	5924d74e-e6e3-4497-afe8-69712c5e4a7a	Điều hoà phòng khách	AC	home/ac_living	{}	2026-06-07 06:58:43.647579+00
af1dad60-6dbd-4093-88c4-d041f3515c17	light_kitchen	9e17fe0c-ab67-49f4-90d6-c5791b1a612c	Đèn bếp	LIGHT	home/light_kitchen	{}	2026-06-07 06:58:43.647579+00
bc48d66a-a277-4b69-979d-897203380a40	sensor_temp	5924d74e-e6e3-4497-afe8-69712c5e4a7a	Cảm biến nhiệt độ	SENSOR	home/sensor_temp	{}	2026-06-07 06:58:43.647579+00
c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	sensor_humid	5924d74e-e6e3-4497-afe8-69712c5e4a7a	Cảm biến độ ẩm	SENSOR	home/sensor_humid	{}	2026-06-07 06:58:43.647579+00
\.


--
-- Data for Name: energy_logs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.energy_logs (id, device_id, power_usage, "timestamp") FROM stdin;
\.


--
-- Data for Name: home_users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.home_users (id, home_id, user_id, role, joined_at) FROM stdin;
1	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	ADMIN	2026-06-07 06:58:43.647579+00
2	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	MEMBER	2026-06-07 06:58:43.647579+00
\.


--
-- Data for Name: homes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.homes (id, name, address, timezone, is_active, created_at) FROM stdin;
3716450c-0d6b-4900-9341-b68b64b44bed	Nhà Hùng - Mai	123 Đường Lê Lợi, TP.HCM	Asia/Ho_Chi_Minh	t	2026-06-07 06:58:43.647579+00
\.


--
-- Data for Name: password_reset_tokens; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.password_reset_tokens (id, user_id, token_hash, expires_at, used_at, created_at) FROM stdin;
\.


--
-- Data for Name: rooms; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.rooms (id, name, icon, image_url, created_at, home_id) FROM stdin;
3fea41ca-7383-4768-9a45-80704d5bbb69	Phòng ngủ	bed	\N	2026-06-07 06:58:43.647579+00	3716450c-0d6b-4900-9341-b68b64b44bed
5924d74e-e6e3-4497-afe8-69712c5e4a7a	Phòng khách	sofa	\N	2026-06-07 06:58:43.647579+00	3716450c-0d6b-4900-9341-b68b64b44bed
9e17fe0c-ab67-49f4-90d6-c5791b1a612c	Bếp	kitchen	\N	2026-06-07 06:58:43.647579+00	3716450c-0d6b-4900-9341-b68b64b44bed
\.


--
-- Data for Name: schedules; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.schedules (id, device_id, name, "time", days_of_week, action_payload, is_active, source_suggestion_id) FROM stdin;
\.


--
-- Data for Name: security_events; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.security_events (id, home_id, event_type, severity, description, "timestamp") FROM stdin;
\.


--
-- Data for Name: sensor_data; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sensor_data ("time", device_id, metric_type, value) FROM stdin;
2026-04-07 17:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-04-07 17:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.7
2026-04-07 18:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.7
2026-04-07 18:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.5
2026-04-07 19:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-04-07 19:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.8
2026-04-07 20:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	24.6
2026-04-07 20:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.2
2026-04-07 21:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.7
2026-04-07 21:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76
2026-04-07 22:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-04-07 22:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.1
2026-04-07 23:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-04-07 23:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.9
2026-04-08 00:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-04-08 00:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-04-08 01:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-04-08 01:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.4
2026-04-08 02:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-04-08 02:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.3
2026-04-08 03:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33
2026-04-08 03:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-04-08 04:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31
2026-04-08 04:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.9
2026-04-08 05:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.7
2026-04-08 05:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.9
2026-04-08 06:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.2
2026-04-08 06:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.4
2026-04-08 07:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.4
2026-04-08 07:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.7
2026-04-08 08:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.9
2026-04-08 08:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.3
2026-04-08 09:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.7
2026-04-08 09:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.8
2026-04-08 10:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.1
2026-04-08 10:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.1
2026-04-08 11:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-04-08 11:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-04-08 12:37:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-04-08 12:37:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.1
2026-04-08 13:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-04-08 13:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.2
2026-04-08 14:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.9
2026-04-08 14:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.3
2026-04-08 15:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-04-08 15:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.4
2026-04-08 16:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-04-08 16:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.9
2026-04-08 17:13:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-04-08 17:13:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.6
2026-04-08 18:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.5
2026-04-08 18:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.3
2026-04-08 19:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-04-08 19:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.4
2026-04-08 20:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-04-08 20:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78
2026-04-08 21:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26
2026-04-08 21:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.8
2026-04-08 22:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-04-08 22:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-04-08 23:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-04-08 23:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.3
2026-04-09 00:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.7
2026-04-09 00:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-04-09 01:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29
2026-04-09 01:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.9
2026-04-09 02:37:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.9
2026-04-09 02:37:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.3
2026-04-09 03:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.4
2026-04-09 03:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-04-09 04:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.5
2026-04-09 04:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.3
2026-04-09 05:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.9
2026-04-09 05:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	65.3
2026-04-09 06:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.2
2026-04-09 06:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-04-09 07:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.8
2026-04-09 07:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.9
2026-04-09 08:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34
2026-04-09 08:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.8
2026-04-09 09:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-04-09 09:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.5
2026-04-09 10:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.8
2026-04-09 10:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.7
2026-04-09 11:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.7
2026-04-09 11:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.8
2026-04-09 12:28:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-04-09 12:28:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.1
2026-04-09 13:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.3
2026-04-09 13:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.2
2026-04-09 14:39:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-04-09 14:39:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.7
2026-04-09 15:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-04-09 15:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.2
2026-04-09 16:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-04-09 16:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.8
2026-04-09 17:37:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-04-09 17:37:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-04-09 18:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-04-09 18:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.2
2026-04-09 19:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-04-09 19:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.3
2026-04-09 20:33:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.9
2026-04-09 20:33:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.6
2026-04-09 21:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-04-09 21:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.1
2026-04-09 22:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-04-09 22:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.3
2026-04-09 23:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-04-09 23:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.2
2026-04-10 00:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-04-10 00:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.6
2026-04-10 01:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-04-10 01:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.9
2026-04-10 02:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.3
2026-04-10 02:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70
2026-04-10 03:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.9
2026-04-10 03:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.6
2026-04-10 04:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.7
2026-04-10 04:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.5
2026-04-10 05:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.3
2026-04-10 05:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.3
2026-04-10 06:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.4
2026-04-10 06:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.2
2026-04-10 07:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.2
2026-04-10 07:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.3
2026-04-10 08:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.1
2026-04-10 08:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.4
2026-04-10 09:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32
2026-04-10 09:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.2
2026-04-10 10:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31
2026-04-10 10:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.8
2026-04-10 11:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.9
2026-04-10 11:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.6
2026-04-10 12:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.7
2026-04-10 12:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.7
2026-04-10 13:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-04-10 13:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.7
2026-04-10 14:28:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-04-10 14:28:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69
2026-04-10 15:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-04-10 15:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	63.8
2026-04-10 16:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-04-10 16:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.3
2026-04-10 17:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-04-10 17:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.9
2026-04-10 18:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-04-10 18:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78
2026-04-10 19:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-04-10 19:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.7
2026-04-10 20:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-04-10 20:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	81.3
2026-04-10 21:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-04-10 21:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.2
2026-04-10 22:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-04-10 22:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.1
2026-04-10 23:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-04-10 23:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.5
2026-04-11 00:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-04-11 00:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-04-11 01:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-04-11 01:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.7
2026-04-11 02:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.5
2026-04-11 02:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72
2026-04-11 03:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.7
2026-04-11 03:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.6
2026-04-11 04:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.7
2026-04-11 04:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-04-11 05:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.5
2026-04-11 05:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.1
2026-04-11 06:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.7
2026-04-11 06:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-04-11 07:55:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.3
2026-04-11 07:55:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.5
2026-04-11 08:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.4
2026-04-11 08:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.4
2026-04-11 09:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.9
2026-04-11 09:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.8
2026-04-11 10:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.5
2026-04-11 10:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.6
2026-04-11 11:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-04-11 11:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.5
2026-04-11 12:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-04-11 12:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.2
2026-04-11 13:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.9
2026-04-11 13:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-04-11 14:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-04-11 14:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.4
2026-04-11 15:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-04-11 15:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.9
2026-04-11 16:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-04-11 16:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.9
2026-04-11 17:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-04-11 17:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.6
2026-04-11 18:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-04-11 18:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.7
2026-04-11 19:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-04-11 19:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.4
2026-04-11 20:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-04-11 20:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.3
2026-04-11 21:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26
2026-04-11 21:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.9
2026-04-11 22:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	24.9
2026-04-11 22:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.2
2026-04-11 23:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-04-11 23:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.9
2026-04-12 00:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.1
2026-04-12 00:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.3
2026-04-12 01:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-04-12 01:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.3
2026-04-12 02:55:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-04-12 02:55:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72
2026-04-12 03:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.7
2026-04-12 03:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.5
2026-04-12 04:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33
2026-04-12 04:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.9
2026-04-12 05:39:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.6
2026-04-12 05:39:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.8
2026-04-12 06:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.1
2026-04-12 06:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.1
2026-04-12 07:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.2
2026-04-12 07:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-04-12 08:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.7
2026-04-12 08:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.7
2026-04-12 09:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.3
2026-04-12 09:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.3
2026-04-12 10:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.7
2026-04-12 10:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.1
2026-04-12 11:35:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.7
2026-04-12 11:35:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.7
2026-04-12 12:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.1
2026-04-12 12:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.2
2026-04-12 13:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-04-12 13:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.7
2026-04-12 14:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-04-12 14:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69
2026-04-12 15:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-04-12 15:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-04-12 16:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-04-12 16:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.7
2026-04-12 17:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-04-12 17:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.6
2026-04-12 18:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-04-12 18:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.9
2026-04-12 19:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-04-12 19:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-04-12 20:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25
2026-04-12 20:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-04-12 21:57:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-04-12 21:57:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.6
2026-04-12 22:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-04-12 22:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.2
2026-04-12 23:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29
2026-04-12 23:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.5
2026-04-13 00:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-04-13 00:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.3
2026-04-13 01:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29
2026-04-13 01:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	81.7
2026-04-13 02:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.7
2026-04-13 02:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.4
2026-04-13 03:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-04-13 03:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-04-13 04:33:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.2
2026-04-13 04:33:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.3
2026-04-13 05:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35
2026-04-13 05:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.5
2026-04-13 06:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.7
2026-04-13 06:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.4
2026-04-13 07:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.8
2026-04-13 07:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.6
2026-04-13 08:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.9
2026-04-13 08:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73
2026-04-13 09:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.1
2026-04-13 09:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.6
2026-04-13 10:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-04-13 10:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.6
2026-04-13 11:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-04-13 11:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-04-13 12:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.5
2026-04-13 12:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.4
2026-04-13 13:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-04-13 13:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.3
2026-04-13 14:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-04-13 14:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.5
2026-04-13 15:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.9
2026-04-13 15:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71
2026-04-13 16:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-04-13 16:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.5
2026-04-13 17:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-04-13 17:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.3
2026-04-13 18:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-04-13 18:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.6
2026-04-13 19:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-04-13 19:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.2
2026-04-13 20:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-04-13 20:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.9
2026-04-13 21:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-04-13 21:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.5
2026-04-13 22:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26
2026-04-13 22:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-04-13 23:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-04-13 23:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.5
2026-04-14 00:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-04-14 00:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.6
2026-04-14 01:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.8
2026-04-14 01:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.1
2026-04-14 02:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.1
2026-04-14 02:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-04-14 03:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31
2026-04-14 03:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.8
2026-04-14 04:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.7
2026-04-14 04:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.3
2026-04-14 05:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.3
2026-04-14 05:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.3
2026-04-14 06:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.9
2026-04-14 06:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77
2026-04-14 07:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.9
2026-04-14 07:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.8
2026-04-14 08:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.5
2026-04-14 08:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.8
2026-04-14 09:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.4
2026-04-14 09:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.4
2026-04-14 10:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.9
2026-04-14 10:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.3
2026-04-14 11:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.8
2026-04-14 11:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.5
2026-04-14 12:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.8
2026-04-14 12:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.3
2026-04-14 13:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-04-14 13:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.4
2026-04-14 14:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.7
2026-04-14 14:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.1
2026-04-14 15:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-04-14 15:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-04-14 16:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-04-14 16:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.9
2026-04-14 17:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.8
2026-04-14 17:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.7
2026-04-14 18:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-04-14 18:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.4
2026-04-14 19:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.1
2026-04-14 19:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.3
2026-04-14 20:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25
2026-04-14 20:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.5
2026-04-14 21:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.1
2026-04-14 21:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73
2026-04-14 22:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-04-14 22:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73
2026-04-14 23:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-04-14 23:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.2
2026-04-15 00:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.1
2026-04-15 00:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-04-15 01:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.9
2026-04-15 01:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.5
2026-04-15 02:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.9
2026-04-15 02:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-04-15 03:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.5
2026-04-15 03:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.9
2026-04-15 04:57:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.5
2026-04-15 04:57:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.4
2026-04-15 05:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.6
2026-04-15 05:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.7
2026-04-15 06:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.7
2026-04-15 06:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.2
2026-04-15 07:55:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.5
2026-04-15 07:55:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.2
2026-04-15 08:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.8
2026-04-15 08:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71
2026-04-15 09:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.1
2026-04-15 09:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.2
2026-04-15 10:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.1
2026-04-15 10:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-04-15 11:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-04-15 11:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.6
2026-04-15 12:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.8
2026-04-15 12:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-04-15 13:35:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-04-15 13:35:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.1
2026-04-15 14:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.8
2026-04-15 14:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.3
2026-04-15 15:35:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-04-15 15:35:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.1
2026-04-15 16:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-04-15 16:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.9
2026-04-15 17:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-04-15 17:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-04-15 18:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.7
2026-04-15 18:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.4
2026-04-15 19:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.6
2026-04-15 19:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.4
2026-04-15 20:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-04-15 20:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.8
2026-04-15 21:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-04-15 21:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.6
2026-04-15 22:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-04-15 22:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.9
2026-04-15 23:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-04-15 23:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.9
2026-04-16 00:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-04-16 00:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-04-16 01:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.5
2026-04-16 01:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.1
2026-04-16 02:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.4
2026-04-16 02:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.1
2026-04-16 03:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.1
2026-04-16 03:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.4
2026-04-16 04:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.8
2026-04-16 04:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.3
2026-04-16 05:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.5
2026-04-16 05:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.4
2026-04-16 06:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.1
2026-04-16 06:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-04-16 07:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.1
2026-04-16 07:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.2
2026-04-16 08:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.6
2026-04-16 08:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.6
2026-04-16 09:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32
2026-04-16 09:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.2
2026-04-16 10:55:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.4
2026-04-16 10:55:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77
2026-04-16 11:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-04-16 11:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.7
2026-04-16 12:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-04-16 12:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-04-16 13:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.1
2026-04-16 13:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.4
2026-04-16 14:33:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-04-16 14:33:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.6
2026-04-16 15:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-04-16 15:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.8
2026-04-16 16:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-04-16 16:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.4
2026-04-16 17:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-04-16 17:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	82.7
2026-04-16 18:39:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-04-16 18:39:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.6
2026-04-16 19:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.8
2026-04-16 19:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.4
2026-04-16 20:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-04-16 20:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73
2026-04-16 21:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-04-16 21:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.2
2026-04-16 22:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-04-16 22:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.6
2026-04-16 23:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-04-16 23:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.2
2026-04-17 00:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-04-17 00:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.4
2026-04-17 01:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.8
2026-04-17 01:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.7
2026-04-17 02:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.7
2026-04-17 02:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.1
2026-04-17 03:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-04-17 03:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.5
2026-04-17 04:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.3
2026-04-17 04:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.6
2026-04-17 05:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.8
2026-04-17 05:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.5
2026-04-17 06:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.7
2026-04-17 06:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.3
2026-04-17 07:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.7
2026-04-17 07:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.4
2026-04-17 08:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.8
2026-04-17 08:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.8
2026-04-17 09:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.3
2026-04-17 09:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.3
2026-04-17 10:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.1
2026-04-17 10:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.5
2026-04-17 11:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.3
2026-04-17 11:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.3
2026-04-17 12:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-04-17 12:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.3
2026-04-17 13:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-04-17 13:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.2
2026-04-17 14:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-04-17 14:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	64.6
2026-04-17 15:37:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-04-17 15:37:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-04-17 16:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-04-17 16:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	65.8
2026-04-17 17:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-04-17 17:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.2
2026-04-17 18:37:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-04-17 18:37:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.8
2026-04-17 19:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-04-17 19:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.5
2026-04-17 20:57:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-04-17 20:57:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.6
2026-04-17 21:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-04-17 21:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.8
2026-04-17 22:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-04-17 22:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.6
2026-04-17 23:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-04-17 23:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.3
2026-04-18 00:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.8
2026-04-18 00:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.2
2026-04-18 01:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-04-18 01:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.1
2026-04-18 02:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.3
2026-04-18 02:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.7
2026-04-18 03:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.9
2026-04-18 03:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.6
2026-04-18 04:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.1
2026-04-18 04:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.8
2026-04-18 05:35:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.9
2026-04-18 05:35:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72
2026-04-18 06:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35
2026-04-18 06:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.5
2026-04-18 07:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.1
2026-04-18 07:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68
2026-04-18 08:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.5
2026-04-18 08:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.6
2026-04-18 09:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.8
2026-04-18 09:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.7
2026-04-18 10:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.4
2026-04-18 10:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.1
2026-04-18 11:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.7
2026-04-18 11:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.3
2026-04-18 12:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.4
2026-04-18 12:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.1
2026-04-18 13:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-04-18 13:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73
2026-04-18 14:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-04-18 14:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.3
2026-04-18 15:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-04-18 15:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	62.4
2026-04-18 16:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.8
2026-04-18 16:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.2
2026-04-18 17:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-04-18 17:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.3
2026-04-18 18:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25
2026-04-18 18:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.3
2026-04-18 19:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-04-18 19:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.3
2026-04-18 20:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-04-18 20:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.6
2026-04-18 21:37:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.4
2026-04-18 21:37:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.8
2026-04-18 22:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-04-18 22:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.9
2026-04-18 23:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-04-18 23:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.6
2026-04-19 00:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-04-19 00:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.6
2026-04-19 01:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-04-19 01:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.8
2026-04-19 02:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.7
2026-04-19 02:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	81.2
2026-04-19 03:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32
2026-04-19 03:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.4
2026-04-19 04:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.8
2026-04-19 04:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.5
2026-04-19 05:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.1
2026-04-19 05:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.2
2026-04-19 06:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.1
2026-04-19 06:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.9
2026-04-19 07:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.4
2026-04-19 07:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.9
2026-04-19 08:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.6
2026-04-19 08:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.5
2026-04-19 09:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.5
2026-04-19 09:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69
2026-04-19 10:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-04-19 10:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.3
2026-04-19 11:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-04-19 11:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.3
2026-04-19 12:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.1
2026-04-19 12:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.7
2026-04-19 13:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.5
2026-04-19 13:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.5
2026-04-19 14:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-04-19 14:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.8
2026-04-19 15:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-04-19 15:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.1
2026-04-19 16:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-04-19 16:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.7
2026-04-19 17:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-04-19 17:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.4
2026-04-19 18:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-04-19 18:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.6
2026-04-19 19:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.1
2026-04-19 19:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.3
2026-04-19 20:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.5
2026-04-19 20:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.6
2026-04-19 21:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.7
2026-04-19 21:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.5
2026-04-19 22:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.1
2026-04-19 22:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-04-19 23:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-04-19 23:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	81.6
2026-04-20 00:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-04-20 00:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.2
2026-04-20 01:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.9
2026-04-20 01:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72
2026-04-20 02:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.3
2026-04-20 02:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.5
2026-04-20 03:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.6
2026-04-20 03:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.9
2026-04-20 04:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.8
2026-04-20 04:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.3
2026-04-20 05:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.7
2026-04-20 05:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.3
2026-04-20 06:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.4
2026-04-20 06:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.1
2026-04-20 07:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.8
2026-04-20 07:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.6
2026-04-20 08:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34
2026-04-20 08:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.6
2026-04-20 09:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.5
2026-04-20 09:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.5
2026-04-20 10:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-04-20 10:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.4
2026-04-20 11:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-04-20 11:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.6
2026-04-20 12:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-04-20 12:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.2
2026-04-20 13:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.8
2026-04-20 13:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.8
2026-04-20 14:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-04-20 14:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.1
2026-04-20 15:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-04-20 15:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.1
2026-04-20 16:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-04-20 16:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68
2026-04-20 17:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-04-20 17:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.9
2026-04-20 18:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-04-20 18:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.2
2026-04-20 19:13:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.7
2026-04-20 19:13:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.1
2026-04-20 20:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26
2026-04-20 20:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.1
2026-04-20 21:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-04-20 21:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.4
2026-04-20 22:37:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-04-20 22:37:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.8
2026-04-20 23:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-04-20 23:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.5
2026-04-21 00:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-04-21 00:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.9
2026-04-21 01:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.9
2026-04-21 01:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.2
2026-04-21 02:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-04-21 02:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.6
2026-04-21 03:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.3
2026-04-21 03:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-04-21 04:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.7
2026-04-21 04:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-04-21 05:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.8
2026-04-21 05:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.3
2026-04-21 06:33:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.2
2026-04-21 06:33:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.9
2026-04-21 07:13:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.4
2026-04-21 07:13:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.9
2026-04-21 08:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.4
2026-04-21 08:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.5
2026-04-21 09:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31
2026-04-21 09:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.6
2026-04-21 10:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.2
2026-04-21 10:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.8
2026-04-21 11:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-04-21 11:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71
2026-04-21 12:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-04-21 12:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.1
2026-04-21 13:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.7
2026-04-21 13:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-04-21 14:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-04-21 14:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	65.4
2026-04-21 15:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-04-21 15:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.2
2026-04-21 16:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-04-21 16:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-04-21 17:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-04-21 17:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-04-21 18:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-04-21 18:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.1
2026-04-21 19:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-04-21 19:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.2
2026-04-21 20:35:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-04-21 20:35:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.7
2026-04-21 21:57:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-04-21 21:57:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76
2026-04-21 22:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-04-21 22:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.3
2026-04-21 23:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-04-21 23:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.4
2026-04-22 00:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.7
2026-04-22 00:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76
2026-04-22 01:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.1
2026-04-22 01:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.1
2026-04-22 02:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-04-22 02:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.4
2026-04-22 03:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.5
2026-04-22 03:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72
2026-04-22 04:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.2
2026-04-22 04:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68
2026-04-22 05:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.2
2026-04-22 05:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.5
2026-04-22 06:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.6
2026-04-22 06:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.8
2026-04-22 07:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.1
2026-04-22 07:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.1
2026-04-22 08:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.3
2026-04-22 08:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.8
2026-04-22 09:33:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32
2026-04-22 09:33:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.2
2026-04-22 10:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.9
2026-04-22 10:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.7
2026-04-22 11:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-04-22 11:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.9
2026-04-22 12:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-04-22 12:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.4
2026-04-22 13:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-04-22 13:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-04-22 14:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-04-22 14:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.8
2026-04-22 15:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-04-22 15:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.2
2026-04-22 16:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-04-22 16:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.9
2026-04-22 17:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-04-22 17:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.7
2026-04-22 18:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-04-22 18:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.9
2026-04-22 19:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-04-22 19:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.1
2026-04-22 20:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26
2026-04-22 20:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.8
2026-04-22 21:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-04-22 21:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-04-22 22:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.7
2026-04-22 22:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.9
2026-04-22 23:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-04-22 23:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.1
2026-04-23 00:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.5
2026-04-23 00:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.7
2026-04-23 01:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-04-23 01:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-04-23 02:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.1
2026-04-23 02:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.7
2026-04-23 03:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.3
2026-04-23 03:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.5
2026-04-23 04:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.8
2026-04-23 04:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.8
2026-04-23 05:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34
2026-04-23 05:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.5
2026-04-23 06:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.5
2026-04-23 06:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.4
2026-04-23 07:55:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.6
2026-04-23 07:55:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.4
2026-04-23 08:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.9
2026-04-23 08:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.3
2026-04-23 09:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.8
2026-04-23 09:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.4
2026-04-23 10:55:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.2
2026-04-23 10:55:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.2
2026-04-23 11:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-04-23 11:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72
2026-04-23 12:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.1
2026-04-23 12:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-04-23 13:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-04-23 13:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	65.7
2026-04-23 14:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.5
2026-04-23 14:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-04-23 15:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-04-23 15:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.9
2026-04-23 16:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-04-23 16:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74
2026-04-23 17:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-04-23 17:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.2
2026-04-23 18:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.9
2026-04-23 18:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78
2026-04-23 19:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.9
2026-04-23 19:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.7
2026-04-23 20:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-04-23 20:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.2
2026-04-23 21:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	24.4
2026-04-23 21:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-04-23 22:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-04-23 22:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74
2026-04-23 23:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-04-23 23:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.1
2026-04-24 00:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-04-24 00:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.5
2026-04-24 01:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.4
2026-04-24 01:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79
2026-04-24 02:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-04-24 02:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.3
2026-04-24 03:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-04-24 03:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-04-24 04:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.9
2026-04-24 04:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.5
2026-04-24 05:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.3
2026-04-24 05:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.4
2026-04-24 06:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.5
2026-04-24 06:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.4
2026-04-24 07:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	36
2026-04-24 07:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.1
2026-04-24 08:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.4
2026-04-24 08:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.1
2026-04-24 09:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.3
2026-04-24 09:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-04-24 10:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.2
2026-04-24 10:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.8
2026-04-24 11:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.4
2026-04-24 11:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.9
2026-04-24 12:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-04-24 12:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.3
2026-04-24 13:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-04-24 13:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.1
2026-04-24 14:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-04-24 14:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.5
2026-04-24 15:55:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-04-24 15:55:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68
2026-04-24 16:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-04-24 16:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70
2026-04-24 17:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-04-24 17:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.8
2026-04-24 18:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-04-24 18:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.9
2026-04-24 19:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-04-24 19:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	81
2026-04-24 20:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-04-24 20:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.2
2026-04-24 21:39:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.9
2026-04-24 21:39:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.3
2026-04-24 22:37:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-04-24 22:37:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.3
2026-04-24 23:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.9
2026-04-24 23:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.2
2026-04-25 00:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-04-25 00:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-04-25 01:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-04-25 01:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.7
2026-04-25 02:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-04-25 02:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.8
2026-04-25 03:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.5
2026-04-25 03:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.7
2026-04-25 04:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.3
2026-04-25 04:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.7
2026-04-25 05:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.1
2026-04-25 05:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.4
2026-04-25 06:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.5
2026-04-25 06:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.6
2026-04-25 07:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.7
2026-04-25 07:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.9
2026-04-25 08:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.3
2026-04-25 08:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.9
2026-04-25 09:57:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31
2026-04-25 09:57:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.6
2026-04-25 10:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-04-25 10:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-04-25 11:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.3
2026-04-25 11:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.3
2026-04-25 12:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.3
2026-04-25 12:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68
2026-04-25 13:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-04-25 13:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.4
2026-04-25 14:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-04-25 14:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.5
2026-04-25 15:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-04-25 15:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	63.4
2026-04-25 16:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-04-25 16:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.6
2026-04-25 17:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-04-25 17:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.5
2026-04-25 18:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-04-25 18:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.2
2026-04-25 19:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-04-25 19:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76
2026-04-25 20:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	24.8
2026-04-25 20:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.6
2026-04-25 21:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-04-25 21:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.7
2026-04-25 22:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-04-25 22:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-04-25 23:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-04-25 23:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.7
2026-04-26 00:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.8
2026-04-26 00:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.9
2026-04-26 01:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-04-26 01:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.1
2026-04-26 02:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.7
2026-04-26 02:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.9
2026-04-26 03:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.7
2026-04-26 03:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.8
2026-04-26 04:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.7
2026-04-26 04:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.1
2026-04-26 05:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.2
2026-04-26 05:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.9
2026-04-26 06:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35
2026-04-26 06:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.4
2026-04-26 07:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.3
2026-04-26 07:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.6
2026-04-26 08:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.5
2026-04-26 08:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.7
2026-04-26 09:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.5
2026-04-26 09:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.9
2026-04-26 10:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.3
2026-04-26 10:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.1
2026-04-26 11:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-04-26 11:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.7
2026-04-26 12:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.7
2026-04-26 12:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.6
2026-04-26 13:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-04-26 13:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.3
2026-04-26 14:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-04-26 14:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.7
2026-04-26 15:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.1
2026-04-26 15:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.3
2026-04-26 16:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-04-26 16:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.7
2026-04-26 17:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-04-26 17:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.7
2026-04-26 18:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.1
2026-04-26 18:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.5
2026-04-26 19:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-04-26 19:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.2
2026-04-26 20:13:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-04-26 20:13:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.8
2026-04-26 21:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-04-26 21:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.5
2026-04-26 22:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.8
2026-04-26 22:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.1
2026-04-26 23:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-04-26 23:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.1
2026-04-27 00:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.7
2026-04-27 00:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-04-27 01:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.7
2026-04-27 01:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.3
2026-04-27 02:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-04-27 02:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79
2026-04-27 03:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.2
2026-04-27 03:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-04-27 04:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.7
2026-04-27 04:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.7
2026-04-27 05:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.9
2026-04-27 05:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.9
2026-04-27 06:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.7
2026-04-27 06:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68
2026-04-27 07:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.5
2026-04-27 07:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.7
2026-04-27 08:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.5
2026-04-27 08:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.9
2026-04-27 09:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.7
2026-04-27 09:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-04-27 10:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.4
2026-04-27 10:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.6
2026-04-27 11:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.8
2026-04-27 11:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.4
2026-04-27 12:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29
2026-04-27 12:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.2
2026-04-27 13:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-04-27 13:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-04-27 14:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-04-27 14:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.5
2026-04-27 15:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-04-27 15:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.7
2026-04-27 16:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-04-27 16:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.1
2026-04-27 17:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.8
2026-04-27 17:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.5
2026-04-27 18:33:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.1
2026-04-27 18:33:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.2
2026-04-27 19:35:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-04-27 19:35:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.6
2026-04-27 20:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.7
2026-04-27 20:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.7
2026-04-27 21:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.9
2026-04-27 21:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.3
2026-04-27 22:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.1
2026-04-27 22:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.4
2026-04-27 23:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-04-27 23:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-04-28 00:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-04-28 00:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-04-28 01:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-04-28 01:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.2
2026-04-28 02:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.3
2026-04-28 02:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-04-28 03:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.7
2026-04-28 03:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-04-28 04:39:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.3
2026-04-28 04:39:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.9
2026-04-28 05:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.4
2026-04-28 05:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.8
2026-04-28 06:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	36.5
2026-04-28 06:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.9
2026-04-28 07:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.5
2026-04-28 07:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-04-28 08:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.3
2026-04-28 08:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.6
2026-04-28 09:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.4
2026-04-28 09:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-04-28 10:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-04-28 10:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.2
2026-04-28 11:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.3
2026-04-28 11:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.3
2026-04-28 12:39:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.9
2026-04-28 12:39:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.3
2026-04-28 13:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-04-28 13:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.7
2026-04-28 14:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-04-28 14:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.3
2026-04-28 15:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-04-28 15:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.3
2026-04-28 16:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-04-28 16:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.1
2026-04-28 17:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-04-28 17:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	81
2026-04-28 18:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-04-28 18:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	82.3
2026-04-28 19:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-04-28 19:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.3
2026-04-28 20:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-04-28 20:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.2
2026-04-28 21:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-04-28 21:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.8
2026-04-28 22:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.7
2026-04-28 22:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.1
2026-04-28 23:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.9
2026-04-28 23:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.1
2026-04-29 00:37:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.5
2026-04-29 00:37:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.2
2026-04-29 01:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-04-29 01:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.6
2026-04-29 02:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.7
2026-04-29 02:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.6
2026-04-29 03:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.3
2026-04-29 03:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.1
2026-04-29 04:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.9
2026-04-29 04:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.2
2026-04-29 05:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.8
2026-04-29 05:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-04-29 06:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.6
2026-04-29 06:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.7
2026-04-29 07:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.5
2026-04-29 07:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.2
2026-04-29 08:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.3
2026-04-29 08:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.7
2026-04-29 09:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.1
2026-04-29 09:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.2
2026-04-29 10:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.6
2026-04-29 10:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.8
2026-04-29 11:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.8
2026-04-29 11:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.2
2026-04-29 12:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.8
2026-04-29 12:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.9
2026-04-29 13:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.7
2026-04-29 13:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.9
2026-04-29 14:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-04-29 14:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.3
2026-04-29 15:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-04-29 15:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.8
2026-04-29 16:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-04-29 16:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.4
2026-04-29 17:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.9
2026-04-29 17:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78
2026-04-29 18:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-04-29 18:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.1
2026-04-29 19:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-04-29 19:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.6
2026-04-29 20:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-04-29 20:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.7
2026-04-29 21:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-04-29 21:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.3
2026-04-29 22:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-04-29 22:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.9
2026-04-29 23:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-04-29 23:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.5
2026-04-30 00:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-04-30 00:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.5
2026-04-30 01:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.3
2026-04-30 01:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.3
2026-04-30 02:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.3
2026-04-30 02:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.1
2026-04-30 03:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.5
2026-04-30 03:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.2
2026-04-30 04:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.6
2026-04-30 04:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.8
2026-04-30 05:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.8
2026-04-30 05:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.4
2026-04-30 06:39:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.7
2026-04-30 06:39:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.7
2026-04-30 07:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.2
2026-04-30 07:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.3
2026-04-30 08:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.7
2026-04-30 08:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.2
2026-04-30 09:35:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.9
2026-04-30 09:35:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-04-30 10:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.8
2026-04-30 10:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.8
2026-04-30 11:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-04-30 11:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	64.8
2026-04-30 12:28:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.1
2026-04-30 12:28:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	63.8
2026-04-30 13:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.3
2026-04-30 13:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.7
2026-04-30 14:39:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-04-30 14:39:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.7
2026-04-30 15:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-04-30 15:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.4
2026-04-30 16:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-04-30 16:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.2
2026-04-30 17:13:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-04-30 17:13:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-04-30 18:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-04-30 18:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-04-30 19:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-04-30 19:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-04-30 20:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.5
2026-04-30 20:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.1
2026-04-30 21:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-04-30 21:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73
2026-04-30 22:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-04-30 22:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-04-30 23:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-04-30 23:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.4
2026-05-01 00:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.8
2026-05-01 00:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.8
2026-05-01 01:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-05-01 01:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-05-01 02:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.5
2026-05-01 02:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.1
2026-05-01 03:33:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.3
2026-05-01 03:33:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-05-01 04:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-05-01 04:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.4
2026-05-01 05:57:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.5
2026-05-01 05:57:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.7
2026-05-01 06:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.7
2026-05-01 06:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.3
2026-05-01 07:28:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.3
2026-05-01 07:28:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.9
2026-05-01 08:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.2
2026-05-01 08:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.2
2026-05-01 09:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.1
2026-05-01 09:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.8
2026-05-01 10:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.3
2026-05-01 10:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.9
2026-05-01 11:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.4
2026-05-01 11:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.8
2026-05-01 12:57:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-05-01 12:57:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.4
2026-05-01 13:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-05-01 13:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	65
2026-05-01 14:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-05-01 14:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.5
2026-05-01 15:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-05-01 15:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.4
2026-05-01 16:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-05-01 16:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.4
2026-05-01 17:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-05-01 17:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.4
2026-05-01 18:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-05-01 18:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.9
2026-05-01 19:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-05-01 19:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.8
2026-05-01 20:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.9
2026-05-01 20:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-05-01 21:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-05-01 21:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.2
2026-05-01 22:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-05-01 22:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.2
2026-05-01 23:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-05-01 23:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.6
2026-05-02 00:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-05-02 00:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.6
2026-05-02 01:33:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-05-02 01:33:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.3
2026-05-02 02:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.8
2026-05-02 02:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-05-02 03:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.8
2026-05-02 03:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72
2026-05-02 04:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.8
2026-05-02 04:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.1
2026-05-02 05:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.1
2026-05-02 05:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.4
2026-05-02 06:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.7
2026-05-02 06:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.6
2026-05-02 07:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.9
2026-05-02 07:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-05-02 08:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.1
2026-05-02 08:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.2
2026-05-02 09:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.8
2026-05-02 09:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.7
2026-05-02 10:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.9
2026-05-02 10:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-05-02 11:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-05-02 11:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.8
2026-05-02 12:37:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-05-02 12:37:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.6
2026-05-02 13:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-05-02 13:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	65.8
2026-05-02 14:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-05-02 14:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.5
2026-05-02 15:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-05-02 15:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.6
2026-05-02 16:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-05-02 16:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.4
2026-05-02 17:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-05-02 17:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79
2026-05-02 18:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-05-02 18:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74
2026-05-02 19:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-05-02 19:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.7
2026-05-02 20:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.7
2026-05-02 20:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.4
2026-05-02 21:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-05-02 21:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.1
2026-05-02 22:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.1
2026-05-02 22:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78
2026-05-02 23:37:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-05-02 23:37:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.1
2026-05-03 00:55:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-05-03 00:55:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.2
2026-05-03 01:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.7
2026-05-03 01:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.3
2026-05-03 02:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.4
2026-05-03 02:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71
2026-05-03 03:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.1
2026-05-03 03:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-05-03 04:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31
2026-05-03 04:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.6
2026-05-03 05:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.3
2026-05-03 05:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.1
2026-05-03 06:13:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.3
2026-05-03 06:13:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.1
2026-05-03 07:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.9
2026-05-03 07:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-05-03 08:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.8
2026-05-03 08:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.5
2026-05-03 09:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.5
2026-05-03 09:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-05-03 10:33:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-05-03 10:33:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.1
2026-05-03 11:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.7
2026-05-03 11:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.7
2026-05-03 12:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.4
2026-05-03 12:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.2
2026-05-03 13:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.6
2026-05-03 13:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.7
2026-05-03 14:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-05-03 14:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.4
2026-05-03 15:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-05-03 15:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.3
2026-05-03 16:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-05-03 16:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.3
2026-05-03 17:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-05-03 17:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.1
2026-05-03 18:57:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-05-03 18:57:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79
2026-05-03 19:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-05-03 19:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.2
2026-05-03 20:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-05-03 20:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.2
2026-05-03 21:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.7
2026-05-03 21:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.6
2026-05-03 22:55:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-05-03 22:55:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74
2026-05-03 23:39:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-05-03 23:39:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.4
2026-05-04 00:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.1
2026-05-04 00:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.1
2026-05-04 01:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.1
2026-05-04 01:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.8
2026-05-04 02:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.4
2026-05-04 02:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.4
2026-05-04 03:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.5
2026-05-04 03:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70
2026-05-04 04:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.1
2026-05-04 04:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.9
2026-05-04 05:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.7
2026-05-04 05:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-05-04 06:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.5
2026-05-04 06:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.9
2026-05-04 07:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.2
2026-05-04 07:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-05-04 08:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.5
2026-05-04 08:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.8
2026-05-04 09:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.4
2026-05-04 09:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.8
2026-05-04 10:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.6
2026-05-04 10:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.1
2026-05-04 11:13:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-05-04 11:13:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.1
2026-05-04 12:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-05-04 12:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.5
2026-05-04 13:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-05-04 13:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.9
2026-05-04 14:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-05-04 14:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.9
2026-05-04 15:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-05-04 15:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.4
2026-05-04 16:55:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-05-04 16:55:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.4
2026-05-04 17:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-05-04 17:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.7
2026-05-04 18:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-05-04 18:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.4
2026-05-04 19:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-05-04 19:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.6
2026-05-04 20:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-05-04 20:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-05-04 21:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-05-04 21:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.9
2026-05-04 22:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-04 22:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77
2026-05-04 23:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-05-04 23:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.6
2026-05-05 00:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.7
2026-05-05 00:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.1
2026-05-05 01:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-05-05 01:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.4
2026-05-05 02:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-05-05 02:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-05-05 03:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.7
2026-05-05 03:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.4
2026-05-05 04:35:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.2
2026-05-05 04:35:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.4
2026-05-05 05:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.8
2026-05-05 05:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.3
2026-05-05 06:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.3
2026-05-05 06:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.6
2026-05-05 07:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.3
2026-05-05 07:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.6
2026-05-05 08:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.6
2026-05-05 08:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.8
2026-05-05 09:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.5
2026-05-05 09:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-05-05 10:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.6
2026-05-05 10:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.2
2026-05-05 11:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-05-05 11:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.9
2026-05-05 12:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.7
2026-05-05 12:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.4
2026-05-05 13:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.8
2026-05-05 13:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.5
2026-05-05 14:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-05-05 14:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.7
2026-05-05 15:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-05-05 15:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.7
2026-05-05 16:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-05-05 16:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.5
2026-05-05 17:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-05-05 17:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	81.3
2026-05-05 18:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-05-05 18:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-05-05 19:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-05-05 19:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.1
2026-05-05 20:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-05-05 20:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.7
2026-05-05 21:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-05-05 21:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.5
2026-05-05 22:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-05 22:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	64.4
2026-05-05 23:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-05-05 23:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.7
2026-05-06 00:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-05-06 00:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.8
2026-05-06 01:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-05-06 01:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.1
2026-05-06 02:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.9
2026-05-06 02:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-05-06 03:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.3
2026-05-06 03:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.6
2026-05-06 04:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.2
2026-05-06 04:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.4
2026-05-06 05:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34
2026-05-06 05:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73
2026-05-06 06:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.6
2026-05-06 06:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.9
2026-05-06 07:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.7
2026-05-06 07:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-05-06 08:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.7
2026-05-06 08:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.5
2026-05-06 09:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.3
2026-05-06 09:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.8
2026-05-06 10:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.4
2026-05-06 10:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.2
2026-05-06 11:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.4
2026-05-06 11:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.5
2026-05-06 12:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.3
2026-05-06 12:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.6
2026-05-06 13:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.7
2026-05-06 13:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.3
2026-05-06 14:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.4
2026-05-06 14:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	62.5
2026-05-06 15:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-05-06 15:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.8
2026-05-06 16:28:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.1
2026-05-06 16:28:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.2
2026-05-06 17:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-05-06 17:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	83.4
2026-05-06 18:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-05-06 18:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	81.7
2026-05-06 19:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-05-06 19:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.7
2026-05-06 20:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-05-06 20:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.9
2026-05-06 21:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-05-06 21:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	82
2026-05-06 22:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.7
2026-05-06 22:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.1
2026-05-06 23:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-05-06 23:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-05-07 00:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-05-07 00:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.2
2026-05-07 01:35:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-05-07 01:35:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79
2026-05-07 02:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.1
2026-05-07 02:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.6
2026-05-07 03:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.7
2026-05-07 03:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.2
2026-05-07 04:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.9
2026-05-07 04:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.4
2026-05-07 05:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.9
2026-05-07 05:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.9
2026-05-07 06:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.9
2026-05-07 06:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.1
2026-05-07 07:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.7
2026-05-07 07:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.9
2026-05-07 08:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.7
2026-05-07 08:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.1
2026-05-07 09:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.8
2026-05-07 09:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.4
2026-05-07 10:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-05-07 10:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.6
2026-05-07 11:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.6
2026-05-07 11:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.3
2026-05-07 12:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-05-07 12:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.7
2026-05-07 13:33:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.1
2026-05-07 13:33:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	64.6
2026-05-07 14:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-05-07 14:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.5
2026-05-07 15:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-05-07 15:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.3
2026-05-07 16:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-05-07 16:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.2
2026-05-07 17:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.8
2026-05-07 17:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.6
2026-05-07 18:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.7
2026-05-07 18:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77
2026-05-07 19:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-05-07 19:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.7
2026-05-07 20:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-05-07 20:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.9
2026-05-07 21:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-07 21:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-05-07 22:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-07 22:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.4
2026-05-07 23:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-05-07 23:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.4
2026-05-08 00:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-05-08 00:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.9
2026-05-08 01:33:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-05-08 01:33:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.5
2026-05-08 02:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.8
2026-05-08 02:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.2
2026-05-08 03:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.1
2026-05-08 03:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71
2026-05-08 04:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.8
2026-05-08 04:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.4
2026-05-08 05:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.4
2026-05-08 05:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.6
2026-05-08 06:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.6
2026-05-08 06:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.8
2026-05-08 07:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.6
2026-05-08 07:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.5
2026-05-08 08:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.2
2026-05-08 08:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.9
2026-05-08 09:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-05-08 09:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.1
2026-05-08 10:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.1
2026-05-08 10:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.1
2026-05-08 11:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.1
2026-05-08 11:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.4
2026-05-08 12:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-05-08 12:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.8
2026-05-08 13:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-05-08 13:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	64.9
2026-05-08 14:39:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.4
2026-05-08 14:39:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.1
2026-05-08 15:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-05-08 15:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67
2026-05-08 16:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-05-08 16:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.1
2026-05-08 17:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-05-08 17:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.2
2026-05-08 18:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-05-08 18:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71
2026-05-08 19:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-05-08 19:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.4
2026-05-08 20:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.4
2026-05-08 20:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.4
2026-05-08 21:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-05-08 21:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	81
2026-05-08 22:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-05-08 22:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.2
2026-05-08 23:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.8
2026-05-08 23:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-05-09 00:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-05-09 00:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.8
2026-05-09 01:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.9
2026-05-09 01:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.5
2026-05-09 02:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-05-09 02:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	81.8
2026-05-09 03:33:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.8
2026-05-09 03:33:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.5
2026-05-09 04:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.1
2026-05-09 04:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79
2026-05-09 05:35:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.5
2026-05-09 05:35:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.8
2026-05-09 06:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.6
2026-05-09 06:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.3
2026-05-09 07:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.4
2026-05-09 07:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.9
2026-05-09 08:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.3
2026-05-09 08:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73
2026-05-09 09:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-05-09 09:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.4
2026-05-09 10:37:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.3
2026-05-09 10:37:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.6
2026-05-09 11:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-05-09 11:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.3
2026-05-09 12:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.8
2026-05-09 12:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.5
2026-05-09 13:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29
2026-05-09 13:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.1
2026-05-09 14:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-05-09 14:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.3
2026-05-09 15:13:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-05-09 15:13:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.1
2026-05-09 16:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-05-09 16:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.2
2026-05-09 17:13:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-09 17:13:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.1
2026-05-09 18:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-05-09 18:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.4
2026-05-09 19:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-05-09 19:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.6
2026-05-09 20:28:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-05-09 20:28:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.6
2026-05-09 21:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.1
2026-05-09 21:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	81.9
2026-05-09 22:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-05-09 22:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.1
2026-05-09 23:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-05-09 23:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.9
2026-05-10 00:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-05-10 00:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.1
2026-05-10 01:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.8
2026-05-10 01:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.5
2026-05-10 02:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.7
2026-05-10 02:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.7
2026-05-10 03:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.9
2026-05-10 03:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.6
2026-05-10 04:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.6
2026-05-10 04:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.5
2026-05-10 05:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.5
2026-05-10 05:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.3
2026-05-10 06:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	36.6
2026-05-10 06:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.9
2026-05-10 07:39:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.4
2026-05-10 07:39:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.4
2026-05-10 08:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.7
2026-05-10 08:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.5
2026-05-10 09:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.1
2026-05-10 09:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.1
2026-05-10 10:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.8
2026-05-10 10:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.2
2026-05-10 11:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.6
2026-05-10 11:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.1
2026-05-10 12:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-05-10 12:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.1
2026-05-10 13:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-05-10 13:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.6
2026-05-10 14:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.5
2026-05-10 14:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.7
2026-05-10 15:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.1
2026-05-10 15:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66
2026-05-10 16:37:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-05-10 16:37:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.5
2026-05-10 17:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-05-10 17:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-05-10 18:39:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-05-10 18:39:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.9
2026-05-10 19:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-05-10 19:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.8
2026-05-10 20:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.6
2026-05-10 20:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-05-10 21:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-10 21:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72
2026-05-10 22:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-05-10 22:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.9
2026-05-10 23:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-05-10 23:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.9
2026-05-11 00:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-05-11 00:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.3
2026-05-11 01:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-05-11 01:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.4
2026-05-11 02:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-05-11 02:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.7
2026-05-11 03:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.5
2026-05-11 03:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-05-11 04:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.3
2026-05-11 04:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.2
2026-05-11 05:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34
2026-05-11 05:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.7
2026-05-11 06:33:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.9
2026-05-11 06:33:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.1
2026-05-11 07:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.5
2026-05-11 07:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.4
2026-05-11 08:28:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.7
2026-05-11 08:28:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.9
2026-05-11 09:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-05-11 09:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72
2026-05-11 10:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.3
2026-05-11 10:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-05-11 11:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.5
2026-05-11 11:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.4
2026-05-11 12:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-05-11 12:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.1
2026-05-11 13:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-05-11 13:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.9
2026-05-11 14:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.8
2026-05-11 14:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.2
2026-05-11 15:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-05-11 15:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.4
2026-05-11 16:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-05-11 16:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.1
2026-05-11 17:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-05-11 17:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71
2026-05-11 18:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-05-11 18:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.3
2026-05-11 19:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-05-11 19:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.3
2026-05-11 20:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-05-11 20:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	81
2026-05-11 21:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-05-11 21:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.9
2026-05-11 22:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-05-11 22:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.4
2026-05-11 23:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-05-11 23:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.2
2026-05-12 00:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.5
2026-05-12 00:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.2
2026-05-12 01:55:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29
2026-05-12 01:55:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.7
2026-05-12 02:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.6
2026-05-12 02:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.2
2026-05-12 03:37:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.1
2026-05-12 03:37:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.9
2026-05-12 04:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.3
2026-05-12 04:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71
2026-05-12 05:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.8
2026-05-12 05:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-05-12 06:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.3
2026-05-12 06:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.8
2026-05-12 07:28:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.2
2026-05-12 07:28:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-05-12 08:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.5
2026-05-12 08:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77
2026-05-12 09:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.1
2026-05-12 09:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.9
2026-05-12 10:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.6
2026-05-12 10:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.3
2026-05-12 11:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-05-12 11:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.6
2026-05-12 12:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-05-12 12:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.5
2026-05-12 13:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-05-12 13:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.4
2026-05-12 14:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-05-12 14:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.8
2026-05-12 15:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.7
2026-05-12 15:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68
2026-05-12 16:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-05-12 16:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.1
2026-05-12 17:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-05-12 17:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.7
2026-05-12 18:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-12 18:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.7
2026-05-12 19:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26
2026-05-12 19:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-05-12 20:57:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-12 20:57:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.6
2026-05-12 21:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-12 21:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.4
2026-05-12 22:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.7
2026-05-12 22:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.9
2026-05-12 23:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.4
2026-05-12 23:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.3
2026-05-13 00:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.7
2026-05-13 00:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.1
2026-05-13 01:33:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.7
2026-05-13 01:33:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-05-13 02:33:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.2
2026-05-13 02:33:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.3
2026-05-13 03:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-05-13 03:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.7
2026-05-13 04:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.6
2026-05-13 04:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.8
2026-05-13 05:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.8
2026-05-13 05:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.3
2026-05-13 06:55:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.9
2026-05-13 06:55:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.7
2026-05-13 07:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.1
2026-05-13 07:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.5
2026-05-13 08:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.1
2026-05-13 08:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.6
2026-05-13 09:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.2
2026-05-13 09:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.1
2026-05-13 10:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.5
2026-05-13 10:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.2
2026-05-13 11:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-05-13 11:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.3
2026-05-13 12:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.8
2026-05-13 12:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.7
2026-05-13 13:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-05-13 13:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.3
2026-05-13 14:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-05-13 14:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.2
2026-05-13 15:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-05-13 15:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	64.9
2026-05-13 16:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-05-13 16:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	65.4
2026-05-13 17:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-13 17:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.3
2026-05-13 18:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-05-13 18:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.5
2026-05-13 19:57:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-05-13 19:57:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74
2026-05-13 20:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-05-13 20:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.9
2026-05-13 21:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-05-13 21:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.2
2026-05-13 22:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-05-13 22:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	81.4
2026-05-13 23:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-05-13 23:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.5
2026-05-14 00:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-05-14 00:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.4
2026-05-14 01:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.9
2026-05-14 01:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.6
2026-05-14 02:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.5
2026-05-14 02:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-05-14 03:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.1
2026-05-14 03:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.5
2026-05-14 04:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.2
2026-05-14 04:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.5
2026-05-14 05:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34
2026-05-14 05:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.8
2026-05-14 06:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.6
2026-05-14 06:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.6
2026-05-14 07:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.2
2026-05-14 07:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.7
2026-05-14 08:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.1
2026-05-14 08:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.5
2026-05-14 09:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.4
2026-05-14 09:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.1
2026-05-14 10:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.8
2026-05-14 10:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.1
2026-05-14 11:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.7
2026-05-14 11:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.5
2026-05-14 12:35:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.8
2026-05-14 12:35:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.1
2026-05-14 13:28:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.9
2026-05-14 13:28:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.1
2026-05-14 14:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.3
2026-05-14 14:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.4
2026-05-14 15:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.5
2026-05-14 15:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.7
2026-05-14 16:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-05-14 16:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.1
2026-05-14 17:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-05-14 17:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.3
2026-05-14 18:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-05-14 18:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.2
2026-05-14 19:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-05-14 19:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.2
2026-05-14 20:13:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-14 20:13:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.2
2026-05-14 21:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-05-14 21:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-05-14 22:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-05-14 22:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.1
2026-05-14 23:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-05-14 23:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-05-15 00:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-05-15 00:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.6
2026-05-15 01:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-05-15 01:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.1
2026-05-15 02:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.5
2026-05-15 02:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.6
2026-05-15 03:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.5
2026-05-15 03:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.6
2026-05-15 04:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.9
2026-05-15 04:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.5
2026-05-15 05:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.2
2026-05-15 05:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.5
2026-05-15 06:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.7
2026-05-15 06:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.5
2026-05-15 07:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.7
2026-05-15 07:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.2
2026-05-15 08:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33
2026-05-15 08:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-05-15 09:13:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.7
2026-05-15 09:13:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.8
2026-05-15 10:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-05-15 10:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.1
2026-05-15 11:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.9
2026-05-15 11:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.9
2026-05-15 12:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-05-15 12:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-05-15 13:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-05-15 13:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.1
2026-05-15 14:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-05-15 14:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.2
2026-05-15 15:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-05-15 15:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.2
2026-05-15 16:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.9
2026-05-15 16:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	64.9
2026-05-15 17:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-05-15 17:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-05-15 18:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-05-15 18:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-05-15 19:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25
2026-05-15 19:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.2
2026-05-15 20:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.1
2026-05-15 20:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.3
2026-05-15 21:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-15 21:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.1
2026-05-15 22:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-05-15 22:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.7
2026-05-15 23:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-05-15 23:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74
2026-05-16 00:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-05-16 00:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.2
2026-05-16 01:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-05-16 01:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.1
2026-05-16 02:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.5
2026-05-16 02:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.4
2026-05-16 03:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.1
2026-05-16 03:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.5
2026-05-16 04:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.5
2026-05-16 04:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.1
2026-05-16 05:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34
2026-05-16 05:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.4
2026-05-16 06:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34
2026-05-16 06:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.7
2026-05-16 07:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.4
2026-05-16 07:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.6
2026-05-16 08:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.5
2026-05-16 08:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.4
2026-05-16 09:28:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32
2026-05-16 09:28:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.3
2026-05-16 10:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.4
2026-05-16 10:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.5
2026-05-16 11:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-05-16 11:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.3
2026-05-16 12:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-05-16 12:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.5
2026-05-16 13:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.4
2026-05-16 13:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.6
2026-05-16 14:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-05-16 14:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.5
2026-05-16 15:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-05-16 15:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.2
2026-05-16 16:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-05-16 16:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.9
2026-05-16 17:55:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-05-16 17:55:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.6
2026-05-16 18:28:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-05-16 18:28:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.7
2026-05-16 19:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-05-16 19:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77
2026-05-16 20:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-05-16 20:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.5
2026-05-16 21:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-05-16 21:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.8
2026-05-16 22:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-05-16 22:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.4
2026-05-16 23:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-05-16 23:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.3
2026-05-17 00:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.8
2026-05-17 00:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.4
2026-05-17 01:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.8
2026-05-17 01:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.4
2026-05-17 02:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-05-17 02:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.5
2026-05-17 03:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.6
2026-05-17 03:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79
2026-05-17 04:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.7
2026-05-17 04:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.6
2026-05-17 05:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.4
2026-05-17 05:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76
2026-05-17 06:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.8
2026-05-17 06:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.9
2026-05-17 07:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.8
2026-05-17 07:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.8
2026-05-17 08:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.6
2026-05-17 08:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.1
2026-05-17 09:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.1
2026-05-17 09:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	65.2
2026-05-17 10:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-05-17 10:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.8
2026-05-17 11:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-05-17 11:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.7
2026-05-17 12:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.3
2026-05-17 12:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.9
2026-05-17 13:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.4
2026-05-17 13:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.5
2026-05-17 14:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.1
2026-05-17 14:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.8
2026-05-17 15:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-05-17 15:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.5
2026-05-17 16:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-05-17 16:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.1
2026-05-17 17:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-05-17 17:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-05-17 18:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-05-17 18:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.2
2026-05-17 19:37:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-05-17 19:37:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.9
2026-05-17 20:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-05-17 20:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.8
2026-05-17 21:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-05-17 21:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.6
2026-05-17 22:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-05-17 22:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.3
2026-05-17 23:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-05-17 23:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-05-18 00:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-05-18 00:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.5
2026-05-18 01:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.7
2026-05-18 01:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.2
2026-05-18 02:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.7
2026-05-18 02:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-05-18 03:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31
2026-05-18 03:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.5
2026-05-18 04:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.8
2026-05-18 04:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72
2026-05-18 05:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.8
2026-05-18 05:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.5
2026-05-18 06:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.5
2026-05-18 06:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.8
2026-05-18 07:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.3
2026-05-18 07:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.2
2026-05-18 08:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.6
2026-05-18 08:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.9
2026-05-18 09:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.1
2026-05-18 09:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.4
2026-05-18 10:57:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.5
2026-05-18 10:57:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.9
2026-05-18 11:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.7
2026-05-18 11:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74
2026-05-18 12:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-05-18 12:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.8
2026-05-18 13:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-05-18 13:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.3
2026-05-18 14:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-05-18 14:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	65.5
2026-05-18 15:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-05-18 15:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.9
2026-05-18 16:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-05-18 16:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.5
2026-05-18 17:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-05-18 17:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.7
2026-05-18 18:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-05-18 18:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.9
2026-05-18 19:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-05-18 19:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.8
2026-05-18 20:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-05-18 20:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.9
2026-05-18 21:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.3
2026-05-18 21:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.9
2026-05-18 22:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-18 22:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.1
2026-05-18 23:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-05-18 23:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.1
2026-05-19 00:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-05-19 00:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.7
2026-05-19 01:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.7
2026-05-19 01:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.6
2026-05-19 02:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.5
2026-05-19 02:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.6
2026-05-19 03:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.7
2026-05-19 03:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.3
2026-05-19 04:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-05-19 04:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-05-19 05:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.3
2026-05-19 05:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.9
2026-05-19 06:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.9
2026-05-19 06:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-05-19 07:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.6
2026-05-19 07:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-05-19 08:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.2
2026-05-19 08:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.8
2026-05-19 09:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.2
2026-05-19 09:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-05-19 10:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.3
2026-05-19 10:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.1
2026-05-19 11:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.8
2026-05-19 11:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.5
2026-05-19 12:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.8
2026-05-19 12:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-05-19 13:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-05-19 13:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.2
2026-05-19 14:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-05-19 14:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.2
2026-05-19 15:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-05-19 15:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.7
2026-05-19 16:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-05-19 16:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	63.4
2026-05-19 17:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-05-19 17:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.3
2026-05-19 18:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-05-19 18:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.6
2026-05-19 19:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.6
2026-05-19 19:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.4
2026-05-19 20:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-05-19 20:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70
2026-05-19 21:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.2
2026-05-19 21:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72
2026-05-19 22:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-05-19 22:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-05-19 23:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.7
2026-05-19 23:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.1
2026-05-20 00:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-05-20 00:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.1
2026-05-20 01:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.4
2026-05-20 01:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	82.5
2026-05-20 02:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-05-20 02:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.9
2026-05-20 03:55:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.2
2026-05-20 03:55:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.3
2026-05-20 04:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.7
2026-05-20 04:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.5
2026-05-20 05:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.1
2026-05-20 05:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.6
2026-05-20 06:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.4
2026-05-20 06:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.7
2026-05-20 07:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33
2026-05-20 07:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.3
2026-05-20 08:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.6
2026-05-20 08:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.6
2026-05-20 09:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31
2026-05-20 09:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69
2026-05-20 10:55:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-05-20 10:55:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.2
2026-05-20 11:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-05-20 11:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.7
2026-05-20 12:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.7
2026-05-20 12:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.7
2026-05-20 13:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-05-20 13:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.6
2026-05-20 14:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-05-20 14:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.3
2026-05-20 15:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-05-20 15:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.6
2026-05-20 16:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-05-20 16:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-05-20 17:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-05-20 17:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.5
2026-05-20 18:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.8
2026-05-20 18:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.8
2026-05-20 19:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-05-20 19:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.3
2026-05-20 20:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-20 20:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.5
2026-05-20 21:57:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.9
2026-05-20 21:57:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.7
2026-05-20 22:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.5
2026-05-20 22:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.3
2026-05-20 23:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-05-20 23:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.4
2026-05-21 00:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.7
2026-05-21 00:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.6
2026-05-21 01:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-05-21 01:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.5
2026-05-21 02:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-05-21 02:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.3
2026-05-21 03:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31
2026-05-21 03:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.5
2026-05-21 04:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.5
2026-05-21 04:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.3
2026-05-21 05:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.3
2026-05-21 05:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.1
2026-05-21 06:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.9
2026-05-21 06:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.3
2026-05-21 07:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.2
2026-05-21 07:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.1
2026-05-21 08:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34
2026-05-21 08:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.2
2026-05-21 09:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32
2026-05-21 09:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.9
2026-05-21 10:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.6
2026-05-21 10:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.7
2026-05-21 11:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.7
2026-05-21 11:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.1
2026-05-21 12:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-05-21 12:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	64.4
2026-05-21 13:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-05-21 13:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.3
2026-05-21 14:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-05-21 14:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.8
2026-05-21 15:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-05-21 15:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.6
2026-05-21 16:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-05-21 16:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.9
2026-05-21 17:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-05-21 17:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.8
2026-05-21 18:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-21 18:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.9
2026-05-21 19:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-05-21 19:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.8
2026-05-21 20:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-05-21 20:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.8
2026-05-21 21:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-21 21:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.3
2026-05-21 22:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-05-21 22:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.7
2026-05-21 23:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-05-21 23:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77
2026-05-22 00:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.8
2026-05-22 00:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.9
2026-05-22 01:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-05-22 01:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.5
2026-05-22 02:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32
2026-05-22 02:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76
2026-05-22 03:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.6
2026-05-22 03:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70
2026-05-22 04:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.2
2026-05-22 04:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.1
2026-05-22 05:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.1
2026-05-22 05:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-05-22 06:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.9
2026-05-22 06:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.8
2026-05-22 07:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.2
2026-05-22 07:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.6
2026-05-22 08:33:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.4
2026-05-22 08:33:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.9
2026-05-22 09:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.5
2026-05-22 09:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.6
2026-05-22 10:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.6
2026-05-22 10:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.2
2026-05-22 11:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.7
2026-05-22 11:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.8
2026-05-22 12:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.1
2026-05-22 12:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.1
2026-05-22 13:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-05-22 13:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.2
2026-05-22 14:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-05-22 14:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.2
2026-05-22 15:13:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-05-22 15:13:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.1
2026-05-22 16:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-05-22 16:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.6
2026-05-22 17:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-05-22 17:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.7
2026-05-22 18:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-05-22 18:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	82.4
2026-05-22 19:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-05-22 19:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.6
2026-05-22 20:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-05-22 20:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.5
2026-05-22 21:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-05-22 21:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.1
2026-05-22 22:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-05-22 22:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72
2026-05-22 23:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-05-22 23:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.8
2026-05-23 00:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.1
2026-05-23 00:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.7
2026-05-23 01:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.7
2026-05-23 01:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.5
2026-05-23 02:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.5
2026-05-23 02:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.9
2026-05-23 03:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.6
2026-05-23 03:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.7
2026-05-23 04:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.8
2026-05-23 04:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.2
2026-05-23 05:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.4
2026-05-23 05:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.8
2026-05-23 06:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.7
2026-05-23 06:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-05-23 07:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.1
2026-05-23 07:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.5
2026-05-23 08:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.5
2026-05-23 08:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.9
2026-05-23 09:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.8
2026-05-23 09:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.6
2026-05-23 10:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.1
2026-05-23 10:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.9
2026-05-23 11:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.2
2026-05-23 11:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.4
2026-05-23 12:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-05-23 12:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.5
2026-05-23 13:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-05-23 13:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	65
2026-05-23 14:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.1
2026-05-23 14:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.5
2026-05-23 15:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-05-23 15:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.6
2026-05-23 16:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-05-23 16:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.7
2026-05-23 17:33:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-05-23 17:33:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.6
2026-05-23 18:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-05-23 18:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-05-23 19:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-05-23 19:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.4
2026-05-23 20:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-05-23 20:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.6
2026-05-23 21:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-05-23 21:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.7
2026-05-23 22:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-05-23 22:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.4
2026-05-23 23:13:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-05-23 23:13:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-05-24 00:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-05-24 00:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.1
2026-05-24 01:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.7
2026-05-24 01:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.3
2026-05-24 02:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.5
2026-05-24 02:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	81.4
2026-05-24 03:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.5
2026-05-24 03:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-05-24 04:33:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.6
2026-05-24 04:33:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.1
2026-05-24 05:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33
2026-05-24 05:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.5
2026-05-24 06:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.8
2026-05-24 06:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79
2026-05-24 07:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.4
2026-05-24 07:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.4
2026-05-24 08:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.7
2026-05-24 08:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.5
2026-05-24 09:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.4
2026-05-24 09:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.4
2026-05-24 10:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32
2026-05-24 10:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	65.2
2026-05-24 11:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29
2026-05-24 11:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.1
2026-05-24 12:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.3
2026-05-24 12:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.1
2026-05-24 13:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-05-24 13:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.1
2026-05-24 14:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-05-24 14:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.8
2026-05-24 15:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.1
2026-05-24 15:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.7
2026-05-24 16:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-05-24 16:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.5
2026-05-24 17:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-05-24 17:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67
2026-05-24 18:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-05-24 18:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.7
2026-05-24 19:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26
2026-05-24 19:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-05-24 20:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-05-24 20:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.7
2026-05-24 21:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-05-24 21:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.4
2026-05-24 22:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-05-24 22:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-05-24 23:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-05-24 23:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76
2026-05-25 00:35:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-05-25 00:35:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.2
2026-05-25 01:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29
2026-05-25 01:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.5
2026-05-25 02:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-05-25 02:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.4
2026-05-25 03:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.6
2026-05-25 03:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74
2026-05-25 04:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.7
2026-05-25 04:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.5
2026-05-25 05:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.7
2026-05-25 05:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.8
2026-05-25 06:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34
2026-05-25 06:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.1
2026-05-25 07:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.8
2026-05-25 07:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.2
2026-05-25 08:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.2
2026-05-25 08:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.5
2026-05-25 09:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.2
2026-05-25 09:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.5
2026-05-25 10:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.8
2026-05-25 10:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.7
2026-05-25 11:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.4
2026-05-25 11:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.2
2026-05-25 12:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-05-25 12:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.3
2026-05-25 13:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-05-25 13:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.1
2026-05-25 14:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-05-25 14:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.7
2026-05-25 15:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-05-25 15:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.8
2026-05-25 16:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-05-25 16:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.9
2026-05-25 17:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-05-25 17:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.6
2026-05-25 18:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-05-25 18:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.6
2026-05-25 19:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26
2026-05-25 19:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77
2026-05-25 20:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-05-25 20:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.5
2026-05-25 21:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-05-25 21:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.5
2026-05-25 22:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-05-25 22:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-05-25 23:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-05-25 23:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74
2026-05-26 00:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-05-26 00:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.1
2026-05-26 01:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.3
2026-05-26 01:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.5
2026-05-26 02:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31
2026-05-26 02:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.5
2026-05-26 03:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.4
2026-05-26 03:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-05-26 04:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-05-26 04:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-05-26 05:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.2
2026-05-26 05:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67
2026-05-26 06:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.5
2026-05-26 06:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.4
2026-05-26 07:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.1
2026-05-26 07:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.6
2026-05-26 08:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34
2026-05-26 08:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.5
2026-05-26 09:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32
2026-05-26 09:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.3
2026-05-26 10:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.3
2026-05-26 10:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.1
2026-05-26 11:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29
2026-05-26 11:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	65.7
2026-05-26 12:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.6
2026-05-26 12:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.6
2026-05-26 13:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-05-26 13:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66
2026-05-26 14:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.7
2026-05-26 14:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.3
2026-05-26 15:57:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-05-26 15:57:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.4
2026-05-26 16:53:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-05-26 16:53:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72
2026-05-26 17:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-05-26 17:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.2
2026-05-26 18:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-05-26 18:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76
2026-05-26 19:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-05-26 19:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.9
2026-05-26 20:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-05-26 20:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74
2026-05-26 21:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-05-26 21:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.6
2026-05-26 22:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-26 22:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.1
2026-05-26 23:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-05-26 23:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	81.6
2026-05-27 00:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-05-27 00:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.1
2026-05-27 01:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-05-27 01:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.4
2026-05-27 02:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.6
2026-05-27 02:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.2
2026-05-27 03:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.4
2026-05-27 03:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.3
2026-05-27 04:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.2
2026-05-27 04:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.4
2026-05-27 05:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.8
2026-05-27 05:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.3
2026-05-27 06:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.8
2026-05-27 06:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.4
2026-05-27 07:57:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.4
2026-05-27 07:57:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-05-27 08:31:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.9
2026-05-27 08:31:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.5
2026-05-27 09:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.1
2026-05-27 09:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-05-27 10:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.9
2026-05-27 10:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.5
2026-05-27 11:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.1
2026-05-27 11:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.1
2026-05-27 12:28:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29
2026-05-27 12:28:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.4
2026-05-27 13:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.5
2026-05-27 13:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.3
2026-05-27 14:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.4
2026-05-27 14:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.4
2026-05-27 15:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-05-27 15:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71
2026-05-27 16:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-05-27 16:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.2
2026-05-27 17:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-05-27 17:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.5
2026-05-27 18:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-05-27 18:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.4
2026-05-27 19:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.9
2026-05-27 19:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78
2026-05-27 20:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-27 20:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.5
2026-05-27 21:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-05-27 21:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.4
2026-05-27 22:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-05-27 22:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.4
2026-05-27 23:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-05-27 23:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-05-28 00:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-05-28 00:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.2
2026-05-28 01:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-05-28 01:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.4
2026-05-28 02:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.9
2026-05-28 02:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-05-28 03:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.1
2026-05-28 03:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.1
2026-05-28 04:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.4
2026-05-28 04:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-05-28 05:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34
2026-05-28 05:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.9
2026-05-28 06:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.4
2026-05-28 06:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71
2026-05-28 07:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.4
2026-05-28 07:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.6
2026-05-28 08:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.5
2026-05-28 08:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.9
2026-05-28 09:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.6
2026-05-28 09:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.9
2026-05-28 10:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.7
2026-05-28 10:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.3
2026-05-28 11:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.6
2026-05-28 11:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.9
2026-05-28 12:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.1
2026-05-28 12:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.5
2026-05-28 13:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.5
2026-05-28 13:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.2
2026-05-28 14:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.3
2026-05-28 14:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.1
2026-05-28 15:39:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.5
2026-05-28 15:39:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-05-28 16:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-05-28 16:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.3
2026-05-28 17:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-05-28 17:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.5
2026-05-28 18:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.1
2026-05-28 18:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77
2026-05-28 19:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-05-28 19:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.7
2026-05-28 20:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-05-28 20:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.6
2026-05-28 21:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-05-28 21:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	82
2026-05-28 22:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.1
2026-05-28 22:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.5
2026-05-28 23:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-05-28 23:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.2
2026-05-29 00:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.8
2026-05-29 00:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-05-29 01:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-05-29 01:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.9
2026-05-29 02:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.4
2026-05-29 02:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.4
2026-05-29 03:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.2
2026-05-29 03:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.1
2026-05-29 04:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.4
2026-05-29 04:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.8
2026-05-29 05:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34
2026-05-29 05:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.2
2026-05-29 06:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.7
2026-05-29 06:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76
2026-05-29 07:13:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.9
2026-05-29 07:13:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72
2026-05-29 08:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.4
2026-05-29 08:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-05-29 09:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34
2026-05-29 09:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74
2026-05-29 10:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.7
2026-05-29 10:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.1
2026-05-29 11:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.7
2026-05-29 11:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.9
2026-05-29 12:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29
2026-05-29 12:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.4
2026-05-29 13:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-05-29 13:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.7
2026-05-29 14:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.7
2026-05-29 14:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.8
2026-05-29 15:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-05-29 15:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.5
2026-05-29 16:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-05-29 16:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	64.1
2026-05-29 17:35:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-05-29 17:35:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.8
2026-05-29 18:28:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.7
2026-05-29 18:28:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.4
2026-05-29 19:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-05-29 19:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.5
2026-05-29 20:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-05-29 20:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.3
2026-05-29 21:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.5
2026-05-29 21:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.9
2026-05-29 22:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-29 22:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	82.6
2026-05-29 23:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-05-29 23:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.6
2026-05-30 00:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-05-30 00:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.5
2026-05-30 01:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31
2026-05-30 01:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.6
2026-05-30 02:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-05-30 02:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.5
2026-05-30 03:35:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.9
2026-05-30 03:35:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.8
2026-05-30 04:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33
2026-05-30 04:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-05-30 05:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.2
2026-05-30 05:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.7
2026-05-30 06:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.4
2026-05-30 06:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.3
2026-05-30 07:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.9
2026-05-30 07:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.1
2026-05-30 08:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.9
2026-05-30 08:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.3
2026-05-30 09:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.5
2026-05-30 09:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.4
2026-05-30 10:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.4
2026-05-30 10:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.2
2026-05-30 11:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31
2026-05-30 11:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.4
2026-05-30 12:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.6
2026-05-30 12:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.6
2026-05-30 13:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-05-30 13:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69
2026-05-30 14:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.6
2026-05-30 14:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.9
2026-05-30 15:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-05-30 15:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.5
2026-05-30 16:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-05-30 16:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.4
2026-05-30 17:56:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.3
2026-05-30 17:56:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.3
2026-05-30 18:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-05-30 18:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-05-30 19:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.7
2026-05-30 19:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-05-30 20:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-05-30 20:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	83.5
2026-05-30 21:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-05-30 21:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.1
2026-05-30 22:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-05-30 22:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.6
2026-05-30 23:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-05-30 23:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.6
2026-05-31 00:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-05-31 00:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.7
2026-05-31 01:55:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.7
2026-05-31 01:55:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.5
2026-05-31 02:13:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.7
2026-05-31 02:13:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.2
2026-05-31 03:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.1
2026-05-31 03:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.9
2026-05-31 04:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33
2026-05-31 04:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.8
2026-05-31 05:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.9
2026-05-31 05:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70
2026-05-31 06:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.8
2026-05-31 06:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.1
2026-05-31 07:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.8
2026-05-31 07:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74
2026-05-31 08:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.8
2026-05-31 08:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.5
2026-05-31 09:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.3
2026-05-31 09:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.2
2026-05-31 10:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.3
2026-05-31 10:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.3
2026-05-31 11:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.8
2026-05-31 11:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.6
2026-05-31 12:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-05-31 12:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.1
2026-05-31 13:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.5
2026-05-31 13:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.4
2026-05-31 14:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-05-31 14:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.7
2026-05-31 15:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-05-31 15:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.3
2026-05-31 16:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.3
2026-05-31 16:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.6
2026-05-31 17:48:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-05-31 17:48:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.7
2026-05-31 18:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-05-31 18:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.8
2026-05-31 19:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-05-31 19:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.7
2026-05-31 20:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.5
2026-05-31 20:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.3
2026-05-31 21:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.1
2026-05-31 21:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.1
2026-05-31 22:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.7
2026-05-31 22:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.4
2026-05-31 23:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-05-31 23:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.7
2026-06-01 00:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-06-01 00:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77
2026-06-01 01:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-06-01 01:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.2
2026-06-01 02:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-06-01 02:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73
2026-06-01 03:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.8
2026-06-01 03:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-06-01 04:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.5
2026-06-01 04:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.1
2026-06-01 05:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.6
2026-06-01 05:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.2
2026-06-01 06:14:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.1
2026-06-01 06:14:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.6
2026-06-01 07:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.8
2026-06-01 07:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.2
2026-06-01 08:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.3
2026-06-01 08:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.4
2026-06-01 09:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.8
2026-06-01 09:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70
2026-06-01 10:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.3
2026-06-01 10:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.1
2026-06-01 11:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.3
2026-06-01 11:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.6
2026-06-01 12:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-06-01 12:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.3
2026-06-01 13:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.9
2026-06-01 13:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.3
2026-06-01 14:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-06-01 14:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.7
2026-06-01 15:11:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-06-01 15:11:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.7
2026-06-01 16:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.4
2026-06-01 16:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66
2026-06-01 17:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-06-01 17:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.9
2026-06-01 18:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-06-01 18:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.5
2026-06-01 19:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-06-01 19:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.8
2026-06-01 20:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.9
2026-06-01 20:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.1
2026-06-01 21:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-06-01 21:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-06-01 22:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.8
2026-06-01 22:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	78.3
2026-06-01 23:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29
2026-06-01 23:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.2
2026-06-02 00:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.7
2026-06-02 00:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.1
2026-06-02 01:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.9
2026-06-02 01:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.5
2026-06-02 02:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.8
2026-06-02 02:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.8
2026-06-02 03:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.9
2026-06-02 03:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-06-02 04:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.1
2026-06-02 04:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71
2026-06-02 05:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.4
2026-06-02 05:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.1
2026-06-02 06:15:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.8
2026-06-02 06:15:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.4
2026-06-02 07:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.2
2026-06-02 07:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.8
2026-06-02 08:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.5
2026-06-02 08:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.5
2026-06-02 09:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.1
2026-06-02 09:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-06-02 10:44:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.2
2026-06-02 10:44:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.7
2026-06-02 11:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-06-02 11:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-06-02 12:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.5
2026-06-02 12:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.5
2026-06-02 13:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-06-02 13:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.3
2026-06-02 14:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-06-02 14:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75
2026-06-02 15:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-06-02 15:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.9
2026-06-02 16:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.3
2026-06-02 16:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.6
2026-06-02 17:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-06-02 17:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.6
2026-06-02 18:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-06-02 18:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	81.4
2026-06-02 19:07:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28
2026-06-02 19:07:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.1
2026-06-02 20:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-06-02 20:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.3
2026-06-02 21:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.6
2026-06-02 21:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79
2026-06-02 22:42:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26
2026-06-02 22:42:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.6
2026-06-02 23:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.6
2026-06-02 23:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.5
2026-06-03 00:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-06-03 00:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.4
2026-06-03 01:00:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.2
2026-06-03 01:00:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.1
2026-06-03 02:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.6
2026-06-03 02:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.7
2026-06-03 03:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.8
2026-06-03 03:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.2
2026-06-03 04:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.7
2026-06-03 04:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.4
2026-06-03 05:28:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.2
2026-06-03 05:28:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.7
2026-06-03 06:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.7
2026-06-03 06:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.6
2026-06-03 07:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35.5
2026-06-03 07:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.6
2026-06-03 08:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.9
2026-06-03 08:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-06-03 09:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.3
2026-06-03 09:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	66.5
2026-06-03 10:35:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.9
2026-06-03 10:35:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.4
2026-06-03 11:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.7
2026-06-03 11:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.3
2026-06-03 12:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.1
2026-06-03 12:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.1
2026-06-03 13:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-06-03 13:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.7
2026-06-03 14:08:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.5
2026-06-03 14:08:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	67.5
2026-06-03 15:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-06-03 15:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.1
2026-06-03 16:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-06-03 16:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.3
2026-06-03 17:04:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-06-03 17:04:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.7
2026-06-03 18:20:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-06-03 18:20:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74
2026-06-03 19:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-06-03 19:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.9
2026-06-03 20:41:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.9
2026-06-03 20:41:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77
2026-06-03 21:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-06-03 21:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.5
2026-06-03 22:54:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.5
2026-06-03 22:54:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.2
2026-06-03 23:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-06-03 23:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.7
2026-06-04 00:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.3
2026-06-04 00:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.2
2026-06-04 01:12:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-06-04 01:12:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73
2026-06-04 02:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.5
2026-06-04 02:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.4
2026-06-04 03:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.9
2026-06-04 03:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.3
2026-06-04 04:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.8
2026-06-04 04:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.6
2026-06-04 05:05:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.1
2026-06-04 05:05:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.1
2026-06-04 06:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.5
2026-06-04 06:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	65.3
2026-06-04 07:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.7
2026-06-04 07:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.3
2026-06-04 08:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.2
2026-06-04 08:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.5
2026-06-04 09:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.7
2026-06-04 09:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.8
2026-06-04 10:47:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.1
2026-06-04 10:47:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-06-04 11:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.6
2026-06-04 11:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.6
2026-06-04 12:24:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-06-04 12:24:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72
2026-06-04 13:02:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.9
2026-06-04 13:02:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.5
2026-06-04 14:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.5
2026-06-04 14:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.5
2026-06-04 15:45:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-06-04 15:45:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.3
2026-06-04 16:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27
2026-06-04 16:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	65.7
2026-06-04 17:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-06-04 17:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.7
2026-06-04 18:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-06-04 18:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.2
2026-06-04 19:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26
2026-06-04 19:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80.6
2026-06-04 20:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-06-04 20:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	80
2026-06-04 21:27:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.7
2026-06-04 21:27:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.8
2026-06-04 22:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.4
2026-06-04 22:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.6
2026-06-04 23:39:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.9
2026-06-04 23:39:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.3
2026-06-05 00:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.8
2026-06-05 00:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.2
2026-06-05 01:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.9
2026-06-05 01:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.9
2026-06-05 02:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.5
2026-06-05 02:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.8
2026-06-05 03:50:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.5
2026-06-05 03:50:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.6
2026-06-05 04:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.3
2026-06-05 04:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.9
2026-06-05 05:10:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	35
2026-06-05 05:10:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-06-05 06:22:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.9
2026-06-05 06:22:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.9
2026-06-05 07:49:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.9
2026-06-05 07:49:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.7
2026-06-05 08:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.6
2026-06-05 08:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.1
2026-06-05 09:59:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.3
2026-06-05 09:59:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.2
2026-06-05 10:36:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-06-05 10:36:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.9
2026-06-05 11:18:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.7
2026-06-05 11:18:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.8
2026-06-05 12:58:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.1
2026-06-05 12:58:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.2
2026-06-05 13:32:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.1
2026-06-05 13:32:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	64.7
2026-06-05 14:23:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.2
2026-06-05 14:23:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.1
2026-06-05 15:28:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.9
2026-06-05 15:28:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.3
2026-06-05 16:43:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.9
2026-06-05 16:43:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.1
2026-06-05 17:03:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.5
2026-06-05 17:03:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.6
2026-06-05 18:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.6
2026-06-05 18:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-06-05 19:06:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.7
2026-06-05 19:06:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	77.9
2026-06-05 20:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.8
2026-06-05 20:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.2
2026-06-05 21:55:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	26.2
2026-06-05 21:55:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.9
2026-06-05 22:29:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	25.8
2026-06-05 22:29:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76
2026-06-05 23:52:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.2
2026-06-05 23:52:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.3
2026-06-06 00:46:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.1
2026-06-06 00:46:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	79.5
2026-06-06 01:25:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-06-06 01:25:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.4
2026-06-06 02:21:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	31.2
2026-06-06 02:21:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.2
2026-06-06 03:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.6
2026-06-06 03:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.2
2026-06-06 04:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33.7
2026-06-06 04:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	75.7
2026-06-06 05:34:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.5
2026-06-06 05:34:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76
2026-06-06 06:40:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.7
2026-06-06 06:40:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	76.7
2026-06-06 07:38:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	34.2
2026-06-06 07:38:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.5
2026-06-06 08:51:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	33
2026-06-06 08:51:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74.7
2026-06-06 09:30:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.1
2026-06-06 09:30:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	74
2026-06-06 10:01:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	32.2
2026-06-06 10:01:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	70.4
2026-06-06 11:17:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30
2026-06-06 11:17:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	73.3
2026-06-06 12:09:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	30.2
2026-06-06 12:09:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	72.4
2026-06-06 13:19:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	29.6
2026-06-06 13:19:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.5
2026-06-06 14:26:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	27.3
2026-06-06 14:26:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	69.8
2026-06-06 15:16:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.1
2026-06-06 15:16:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	71.1
2026-06-06 16:57:00+00	bc48d66a-a277-4b69-979d-897203380a40	TEMP	28.4
2026-06-06 16:57:00+00	c6f829f5-fca0-4c1e-bb92-e7fe4287ff31	HUMIDITY	68.3
\.


--
-- Data for Name: suggestion_decision_logs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.suggestion_decision_logs (id, pattern_id, home_id, user_id, decision_score, should_suggest, blocked_by, cooldown_signature, metadata_json, created_at) FROM stdin;
160	82	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.58	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 1.0, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.459012+00
161	83	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.58	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 1.0, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["duration_above_baseline", "high_weekly_repetition"]}	2026-06-07 15:06:57.47811+00
162	84	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.585	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.95, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["duration_above_baseline", "high_weekly_repetition"]}	2026-06-07 15:06:57.482221+00
163	85	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.538	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.86, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.486959+00
164	86	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.508	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.76, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.491736+00
165	87	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.501	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.67, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.496133+00
166	88	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.481	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.67, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.500392+00
167	89	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.481	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.67, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.504184+00
168	90	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.501	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.67, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.508057+00
169	91	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.451	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.57, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.511873+00
170	92	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.451	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.57, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.515642+00
171	93	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.444	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["duration_above_baseline", "high_weekly_repetition"]}	2026-06-07 15:06:57.519277+00
172	94	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.444	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.522815+00
173	95	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.424	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.52629+00
174	96	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.424	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["duration_above_baseline", "high_weekly_repetition"]}	2026-06-07 15:06:57.53046+00
175	97	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.474	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device", "high_weekly_repetition"]}	2026-06-07 15:06:57.534656+00
176	98	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.444	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.538213+00
177	99	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.387	f	USELESS	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:06:57.541932+00
178	100	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.367	f	USELESS	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:06:57.545569+00
179	101	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.367	f	USELESS	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:06:57.549308+00
180	102	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.367	f	USELESS	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:06:57.552848+00
181	103	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.367	f	USELESS	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:06:57.556532+00
182	104	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.417	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device"]}	2026-06-07 15:06:57.560239+00
183	105	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.4401	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.4205, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 0.7}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:06:57.563727+00
184	106	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.4365	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.4858, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 0.5}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:06:57.566452+00
185	54	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.58	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 1.0, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.569117+00
186	55	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.565	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.95, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.572977+00
187	56	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.615	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.95, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device", "high_weekly_repetition"]}	2026-06-07 15:06:57.57673+00
188	57	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.558	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.86, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.581213+00
189	58	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.538	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.86, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.587156+00
190	59	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.588	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.86, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device", "high_weekly_repetition"]}	2026-06-07 15:06:57.59237+00
191	60	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.558	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.76, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device", "unusual_hour", "high_weekly_repetition"]}	2026-06-07 15:06:57.597544+00
192	61	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.451	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.57, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.602188+00
193	62	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.501	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.57, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device", "high_weekly_repetition"]}	2026-06-07 15:06:57.607549+00
194	63	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.451	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.57, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.613416+00
195	64	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.471	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.57, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.618112+00
196	65	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.474	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["duration_above_baseline", "energy_heavy_device", "high_weekly_repetition"]}	2026-06-07 15:06:57.622116+00
197	66	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.424	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["unusual_hour", "high_weekly_repetition"]}	2026-06-07 15:06:57.625984+00
198	67	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.424	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.630141+00
199	68	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.394	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.38, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["unusual_hour", "high_weekly_repetition"]}	2026-06-07 15:06:57.63433+00
200	69	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.394	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.38, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.63815+00
201	70	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.394	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.38, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:06:57.641872+00
202	71	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.444	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.38, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device", "high_weekly_repetition"]}	2026-06-07 15:06:57.646141+00
203	72	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.387	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["unusual_hour"]}	2026-06-07 15:06:57.651045+00
204	73	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.367	f	USELESS	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:06:57.656353+00
205	74	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.417	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device"]}	2026-06-07 15:06:57.661667+00
206	75	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.387	f	USELESS	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:06:57.666851+00
207	76	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.387	f	USELESS	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:06:57.671284+00
208	77	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.4401	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.4205, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 0.7}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:06:57.675888+00
209	78	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.396	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.3239, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 0.5}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:06:57.679003+00
210	79	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.4619	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.3875, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 1.0}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:06:57.682178+00
211	80	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.3997	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.3388, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 0.5}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:06:57.685212+00
212	81	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.4018	f	LOW_SCORE	\N	{"threshold": 0.65, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.3474, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 0.5}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:06:57.688067+00
213	82	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.58	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 1.0, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.659533+00
214	83	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.58	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 1.0, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["duration_above_baseline", "high_weekly_repetition"]}	2026-06-07 15:07:15.68383+00
215	84	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.585	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.95, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["duration_above_baseline", "high_weekly_repetition"]}	2026-06-07 15:07:15.689177+00
216	85	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.538	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.86, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.693493+00
217	86	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.508	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.76, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.697284+00
218	87	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.501	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.67, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.700917+00
219	88	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.481	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.67, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.704421+00
220	89	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.481	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.67, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.707952+00
221	90	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.501	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.67, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.71121+00
222	91	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.451	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.57, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.714385+00
223	92	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.451	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.57, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.717731+00
224	93	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.444	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["duration_above_baseline", "high_weekly_repetition"]}	2026-06-07 15:07:15.721218+00
225	94	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.444	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.724743+00
226	95	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.424	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.728357+00
227	96	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.424	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["duration_above_baseline", "high_weekly_repetition"]}	2026-06-07 15:07:15.731799+00
228	97	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.474	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device", "high_weekly_repetition"]}	2026-06-07 15:07:15.735413+00
229	98	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.444	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.738854+00
230	99	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.387	f	USELESS	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:07:15.742534+00
231	100	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.367	f	USELESS	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:07:15.746404+00
232	101	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.367	f	USELESS	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:07:15.750076+00
233	102	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.367	f	USELESS	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:07:15.753547+00
234	103	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.367	f	USELESS	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:07:15.75701+00
235	104	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.417	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device"]}	2026-06-07 15:07:15.760894+00
236	105	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.4401	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.4205, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 0.7}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:07:15.764732+00
237	106	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.4365	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.4858, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 0.5}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:07:15.767794+00
238	54	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.58	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 1.0, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.770761+00
239	55	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.565	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.95, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.774124+00
240	56	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.615	t	\N	TIME_HABIT:ac_bedroom:energy_heavy_device,high_weekly_repetition	{"threshold": 0.6, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "high_energy_device", "repeated_occurrence"], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.95, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device", "high_weekly_repetition"]}	2026-06-07 15:07:15.777603+00
241	57	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.558	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.86, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.783507+00
242	58	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.538	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.86, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.786853+00
243	59	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.588	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.86, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device", "high_weekly_repetition"]}	2026-06-07 15:07:15.790643+00
244	60	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.558	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.76, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device", "unusual_hour", "high_weekly_repetition"]}	2026-06-07 15:07:15.795872+00
245	61	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.451	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.57, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.800679+00
246	62	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.501	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.57, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device", "high_weekly_repetition"]}	2026-06-07 15:07:15.80506+00
247	63	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.451	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.57, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.809344+00
248	64	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.471	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.57, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.813334+00
249	65	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.474	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["duration_above_baseline", "energy_heavy_device", "high_weekly_repetition"]}	2026-06-07 15:07:15.817184+00
250	66	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.424	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["unusual_hour", "high_weekly_repetition"]}	2026-06-07 15:07:15.821387+00
251	67	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.424	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.825218+00
252	68	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.394	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.38, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["unusual_hour", "high_weekly_repetition"]}	2026-06-07 15:07:15.828843+00
253	69	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.394	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.38, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.83246+00
254	70	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.394	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.38, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:15.836246+00
255	71	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.444	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.38, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device", "high_weekly_repetition"]}	2026-06-07 15:07:15.839796+00
256	72	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.387	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["unusual_hour"]}	2026-06-07 15:07:15.842917+00
257	73	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.367	f	USELESS	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:07:15.846229+00
258	74	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.417	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device"]}	2026-06-07 15:07:15.849508+00
259	75	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.387	f	USELESS	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:07:15.852641+00
260	76	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.387	f	USELESS	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:07:15.856252+00
261	77	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.4401	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.4205, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 0.7}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:07:15.860198+00
262	78	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.396	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.3239, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 0.5}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:07:15.862818+00
263	79	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.4619	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.3875, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 1.0}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:07:15.865651+00
264	80	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.3997	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.3388, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 0.5}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:07:15.868267+00
265	81	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.4018	f	LOW_SCORE	\N	{"threshold": 0.6, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.3474, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 0.5}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:07:15.871141+00
266	82	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.58	t	\N	TIME_HABIT:light_kitchen:high_weekly_repetition	{"threshold": 0.55, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "repeated_occurrence"], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 1.0, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:19.957451+00
267	83	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.58	t	\N	TIME_HABIT:light_bedroom:duration_above_baseline,high_weekly_repetition	{"threshold": 0.55, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "duration_above_baseline", "repeated_occurrence"], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 1.0, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["duration_above_baseline", "high_weekly_repetition"]}	2026-06-07 15:07:19.980209+00
268	84	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.585	t	\N	TIME_HABIT:fan_living:duration_above_baseline,high_weekly_repetition	{"threshold": 0.55, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "duration_above_baseline", "repeated_occurrence"], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.95, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["duration_above_baseline", "high_weekly_repetition"]}	2026-06-07 15:07:19.986012+00
269	85	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.538	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.86, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:19.990908+00
270	86	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.508	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.76, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:19.995555+00
271	87	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.501	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.67, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:19.999765+00
272	88	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.481	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.67, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:20.003713+00
273	89	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.481	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.67, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:20.007618+00
274	90	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.501	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.67, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:20.012417+00
275	91	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.451	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.57, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:20.016168+00
276	92	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.451	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.57, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:20.019862+00
277	93	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.444	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["duration_above_baseline", "high_weekly_repetition"]}	2026-06-07 15:07:20.02355+00
278	94	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.444	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:20.02732+00
279	95	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.424	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:20.030966+00
280	96	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.424	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["duration_above_baseline", "high_weekly_repetition"]}	2026-06-07 15:07:20.034482+00
281	97	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.474	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device", "high_weekly_repetition"]}	2026-06-07 15:07:20.038019+00
282	98	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.444	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:20.042125+00
283	99	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.387	f	USELESS	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:07:20.045714+00
284	100	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.367	f	USELESS	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:07:20.049391+00
285	101	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.367	f	USELESS	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:07:20.053099+00
286	102	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.367	f	USELESS	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:07:20.056582+00
287	103	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.367	f	USELESS	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:07:20.06019+00
288	104	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.417	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device"]}	2026-06-07 15:07:20.063775+00
289	105	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.4401	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.4205, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 0.7}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:07:20.067333+00
290	106	3716450c-0d6b-4900-9341-b68b64b44bed	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	0.4365	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.4858, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 0.5}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:07:20.070289+00
291	54	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.58	t	\N	TIME_HABIT:light_kitchen:high_weekly_repetition	{"threshold": 0.55, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "repeated_occurrence"], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 1.0, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:20.073052+00
292	55	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.565	t	\N	TIME_HABIT:light_bedroom:high_weekly_repetition	{"threshold": 0.55, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "repeated_occurrence"], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.95, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:20.078174+00
293	56	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.615	t	\N	TIME_HABIT:ac_bedroom:energy_heavy_device,high_weekly_repetition	{"threshold": 0.55, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "high_energy_device", "repeated_occurrence"], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.95, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device", "high_weekly_repetition"]}	2026-06-07 15:07:20.082473+00
294	57	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.558	t	\N	TIME_HABIT:fan_bedroom:high_weekly_repetition	{"threshold": 0.55, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "repeated_occurrence"], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.86, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:20.086881+00
295	58	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.538	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.86, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:20.091144+00
296	59	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.588	t	\N	TIME_HABIT:ac_living:energy_heavy_device,high_weekly_repetition	{"threshold": 0.55, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "high_energy_device", "repeated_occurrence"], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.86, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device", "high_weekly_repetition"]}	2026-06-07 15:07:20.094903+00
297	60	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.558	t	\N	TIME_HABIT:ac_bedroom:energy_heavy_device,high_weekly_repetition,unusual_hour	{"threshold": 0.55, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "high_energy_device", "unusual_hour", "repeated_occurrence"], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.76, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device", "unusual_hour", "high_weekly_repetition"]}	2026-06-07 15:07:20.099779+00
298	61	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.451	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.57, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:20.104383+00
299	62	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.501	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.57, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device", "high_weekly_repetition"]}	2026-06-07 15:07:20.108115+00
300	63	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.451	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.57, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:20.111842+00
301	64	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.471	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.57, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:20.115883+00
302	65	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.474	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["duration_above_baseline", "energy_heavy_device", "high_weekly_repetition"]}	2026-06-07 15:07:20.120147+00
303	66	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.424	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["unusual_hour", "high_weekly_repetition"]}	2026-06-07 15:07:20.124272+00
304	67	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.424	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.48, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:20.128354+00
305	68	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.394	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.38, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["unusual_hour", "high_weekly_repetition"]}	2026-06-07 15:07:20.132375+00
306	69	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.394	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.38, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:20.136868+00
307	70	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.394	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.38, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": ["high_weekly_repetition"]}	2026-06-07 15:07:20.140852+00
308	71	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.444	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.38, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device", "high_weekly_repetition"]}	2026-06-07 15:07:20.144858+00
309	72	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.387	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": ["unusual_hour"]}	2026-06-07 15:07:20.148617+00
310	73	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.367	f	USELESS	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.4}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:07:20.152522+00
311	74	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.417	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.9}, "cooldown_reasons": [], "usefulness_reasons": ["energy_heavy_device"]}	2026-06-07 15:07:20.156076+00
312	75	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.387	f	USELESS	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:07:20.160237+00
313	76	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.387	f	USELESS	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.4, "user_preference": 0.75, "anomaly_severity": 0.2, "pattern_confidence": 0.29, "historical_acceptance": 0.5, "energy_saving_potential": 0.6}, "cooldown_reasons": [], "usefulness_reasons": []}	2026-06-07 15:07:20.165904+00
314	77	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.4401	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.4205, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 0.7}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:07:20.170392+00
315	78	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.396	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.3239, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 0.5}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:07:20.173554+00
316	79	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.4619	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.3875, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 1.0}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:07:20.176558+00
317	80	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.3997	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.3388, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 0.5}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:07:20.179501+00
318	81	3716450c-0d6b-4900-9341-b68b64b44bed	910adcc3-fd19-48e5-8cdc-13e16cf212f7	0.4018	f	LOW_SCORE	\N	{"threshold": 0.55, "priority_reason": [], "score_breakdown": {"urgency": 0.6, "user_preference": 0.7, "anomaly_severity": 0.3474, "pattern_confidence": 0.2, "historical_acceptance": 0.5, "energy_saving_potential": 0.5}, "cooldown_reasons": [], "usefulness_reasons": ["single_anomaly"]}	2026-06-07 15:07:20.182211+00
\.


--
-- Data for Name: suggestion_feedback_logs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.suggestion_feedback_logs (id, suggestion_id, user_id, feedback_type, feedback_reason, feedback_time, created_at) FROM stdin;
\.


--
-- Data for Name: suggestion_logs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.suggestion_logs (id, user_id, pattern_id, action_type, suggestion_text, suggestion_json, was_accepted, created_at) FROM stdin;
10	910adcc3-fd19-48e5-8cdc-13e16cf212f7	56	SCHEDULE	Tạo lịch bật điều hòa vào ban đêm: Theo thói quen của bạn, điều hòa sẽ tự động được bật vào mỗi tối từ 22h các ngày Thứ 2 đến Thứ 6. Chúng tôi đề xuất tạo lịch để đảm bảo điều này luôn diễn ra đúng giờ.	{"title": "Tạo lịch bật điều hòa vào ban đêm", "source": {"user_name": "Nguyễn Văn Hùng", "pattern_id": 56, "pattern_type": "TIME_HABIT"}, "device_id": "b29217ff-2b22-4cdb-a25e-828ba5011266", "action_type": "SCHEDULE", "description": "Theo thói quen của bạn, điều hòa sẽ tự động được bật vào mỗi tối từ 22h các ngày Thứ 2 đến Thứ 6. Chúng tôi đề xuất tạo lịch để đảm bảo điều này luôn diễn ra đúng giờ.", "device_name": "Điều hoà phòng ngủ", "device_slug": "ac_bedroom", "explanation": {"threshold": 0.55, "usefulness": true, "cooldown_pass": true, "priority_rank": null, "decision_score": 0.615, "priority_score": null, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "high_energy_device", "repeated_occurrence"], "cooldown_reasons": [], "cooldown_signature": "TIME_HABIT:ac_bedroom:energy_heavy_device,high_weekly_repetition", "usefulness_reasons": ["energy_heavy_device", "high_weekly_repetition"], "priority_hard_override": false}, "schedule_payload": {"time": "22:00", "days_of_week": [1, 2, 3, 4, 5], "action_payload": {"power": "ON"}}}	\N	2026-06-07 15:07:25.238895+00
11	910adcc3-fd19-48e5-8cdc-13e16cf212f7	59	SCHEDULE	Tạo lịch bật điều hòa vào buổi tối: Nguyễn Văn Hùng có thói quen bật điều hòa phòng khách vào mỗi chiều Chủ nhật, Thứ 5 và Thứ 7. Chúng tôi đề xuất tạo lịch để thiết bị tự động hoạt động theo thời gian này.	{"title": "Tạo lịch bật điều hòa vào buổi tối", "source": {"user_name": "Nguyễn Văn Hùng", "pattern_id": 59, "pattern_type": "TIME_HABIT"}, "device_id": "6cb5a041-7821-4ca8-8c2c-15363bc35047", "action_type": "SCHEDULE", "description": "Nguyễn Văn Hùng có thói quen bật điều hòa phòng khách vào mỗi chiều Chủ nhật, Thứ 5 và Thứ 7. Chúng tôi đề xuất tạo lịch để thiết bị tự động hoạt động theo thời gian này.", "device_name": "Điều hoà phòng khách", "device_slug": "ac_living", "explanation": {"threshold": 0.55, "usefulness": true, "cooldown_pass": true, "priority_rank": null, "decision_score": 0.588, "priority_score": null, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "high_energy_device", "repeated_occurrence"], "cooldown_reasons": [], "cooldown_signature": "TIME_HABIT:ac_living:energy_heavy_device,high_weekly_repetition", "usefulness_reasons": ["energy_heavy_device", "high_weekly_repetition"], "priority_hard_override": false}, "schedule_payload": {"time": "19:00", "days_of_week": [0, 4, 6], "action_payload": {"power": "ON"}}}	\N	2026-06-07 15:07:25.238895+00
12	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	84	SCHEDULE	Tạo lịch bật quạt phòng khách vào sáng Chủ nhật đến thứ Tư: Bật quạt phòng khách lúc 09:00 các ngày Chủ Nhật, Thứ Hai, Thứ Ba, Thứ Tư để tận dụng thời gian hiệu quả và thoải mái hơn.	{"title": "Tạo lịch bật quạt phòng khách vào sáng Chủ nhật đến thứ Tư", "source": {"user_name": "Trần Thị Mai", "pattern_id": 84, "pattern_type": "TIME_HABIT"}, "device_id": "ef359599-bea0-4f11-8de4-f6c433fbc7fb", "action_type": "SCHEDULE", "description": "Bật quạt phòng khách lúc 09:00 các ngày Chủ Nhật, Thứ Hai, Thứ Ba, Thứ Tư để tận dụng thời gian hiệu quả và thoải mái hơn.", "device_name": "Quạt phòng khách", "device_slug": "fan_living", "explanation": {"threshold": 0.55, "usefulness": true, "cooldown_pass": true, "priority_rank": null, "decision_score": 0.585, "priority_score": null, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "duration_above_baseline", "repeated_occurrence"], "cooldown_reasons": [], "cooldown_signature": "TIME_HABIT:fan_living:duration_above_baseline,high_weekly_repetition", "usefulness_reasons": ["duration_above_baseline", "high_weekly_repetition"], "priority_hard_override": false}, "schedule_payload": {"time": "09:00", "days_of_week": [0, 1, 2, 3, 6], "action_payload": {"power": "ON"}}}	\N	2026-06-07 15:07:25.238895+00
13	910adcc3-fd19-48e5-8cdc-13e16cf212f7	54	SCHEDULE	Tự động bật đèn bếp vào buổi sáng: Theo thói quen của bạn, đèn bếp sẽ tự động được bật vào mỗi buổi sáng từ Thứ 2 đến Thứ 6 lúc 06:00. Đây là một cách giúp cuộc sống hàng ngày trở nên tiện lợi hơn.	{"title": "Tự động bật đèn bếp vào buổi sáng", "source": {"user_name": "Nguyễn Văn Hùng", "pattern_id": 54, "pattern_type": "TIME_HABIT"}, "device_id": "af1dad60-6dbd-4093-88c4-d041f3515c17", "action_type": "SCHEDULE", "description": "Theo thói quen của bạn, đèn bếp sẽ tự động được bật vào mỗi buổi sáng từ Thứ 2 đến Thứ 6 lúc 06:00. Đây là một cách giúp cuộc sống hàng ngày trở nên tiện lợi hơn.", "device_name": "Đèn bếp", "device_slug": "light_kitchen", "explanation": {"threshold": 0.55, "usefulness": true, "cooldown_pass": true, "priority_rank": null, "decision_score": 0.58, "priority_score": null, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "repeated_occurrence"], "cooldown_reasons": [], "cooldown_signature": "TIME_HABIT:light_kitchen:high_weekly_repetition", "usefulness_reasons": ["high_weekly_repetition"], "priority_hard_override": false}, "schedule_payload": {"time": "06:00", "days_of_week": [1, 2, 3, 4, 5], "action_payload": {"power": "ON"}}}	\N	2026-06-07 15:07:25.238895+00
14	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	83	SCHEDULE	Tự động bật đèn phòng ngủ vào buổi chiều: Để tạo thói quen tốt, đèn phòng ngủ sẽ tự động bật vào các ngày Thứ 2, Thứ 3, Thứ 5 và Thứ 6 lúc 14:00. Hãy cùng tận hưởng không gian dịu nhẹ của đêm.	{"title": "Tự động bật đèn phòng ngủ vào buổi chiều", "source": {"user_name": "Trần Thị Mai", "pattern_id": 83, "pattern_type": "TIME_HABIT"}, "device_id": "aacca680-7fa2-41e3-996b-c15a56718f9d", "action_type": "SCHEDULE", "description": "Để tạo thói quen tốt, đèn phòng ngủ sẽ tự động bật vào các ngày Thứ 2, Thứ 3, Thứ 5 và Thứ 6 lúc 14:00. Hãy cùng tận hưởng không gian dịu nhẹ của đêm.", "device_name": "Đèn phòng ngủ", "device_slug": "light_bedroom", "explanation": {"threshold": 0.55, "usefulness": true, "cooldown_pass": true, "priority_rank": null, "decision_score": 0.58, "priority_score": null, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "duration_above_baseline", "repeated_occurrence"], "cooldown_reasons": [], "cooldown_signature": "TIME_HABIT:light_bedroom:duration_above_baseline,high_weekly_repetition", "usefulness_reasons": ["duration_above_baseline", "high_weekly_repetition"], "priority_hard_override": false}, "schedule_payload": {"time": "14:00", "days_of_week": [1, 2, 4, 5], "action_payload": {"power": "ON"}}}	\N	2026-06-07 15:07:25.238895+00
15	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	82	SCHEDULE	Tự động bật đèn bếp vào buổi tối: Để đảm bảo an toàn và tiện lợi khi nấu nướng, chúng tôi sẽ tự động bật đèn bếp lúc 11h các ngày từ thứ 2 đến thứ 6.	{"title": "Tự động bật đèn bếp vào buổi tối", "source": {"user_name": "Trần Thị Mai", "pattern_id": 82, "pattern_type": "TIME_HABIT"}, "device_id": "af1dad60-6dbd-4093-88c4-d041f3515c17", "action_type": "SCHEDULE", "description": "Để đảm bảo an toàn và tiện lợi khi nấu nướng, chúng tôi sẽ tự động bật đèn bếp lúc 11h các ngày từ thứ 2 đến thứ 6.", "device_name": "Đèn bếp", "device_slug": "light_kitchen", "explanation": {"threshold": 0.55, "usefulness": true, "cooldown_pass": true, "priority_rank": null, "decision_score": 0.58, "priority_score": null, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "repeated_occurrence"], "cooldown_reasons": [], "cooldown_signature": "TIME_HABIT:light_kitchen:high_weekly_repetition", "usefulness_reasons": ["high_weekly_repetition"], "priority_hard_override": false}, "schedule_payload": {"time": "11:00", "days_of_week": [1, 2, 3, 4, 5], "action_payload": {"power": "ON"}}}	\N	2026-06-07 15:07:25.238895+00
16	910adcc3-fd19-48e5-8cdc-13e16cf212f7	55	SCHEDULE	Tạo lịch bật đèn phòng ngủ: Theo thói quen của bạn, đèn phòng ngủ sẽ tự động được bật vào mỗi chiều thứ 2, thứ 3, thứ 5 và thứ 6 lúc 22h. Chúng tôi đã lập lịch cho bạn để đảm bảo không bỏ sót.	{"title": "Tạo lịch bật đèn phòng ngủ", "source": {"user_name": "Nguyễn Văn Hùng", "pattern_id": 55, "pattern_type": "TIME_HABIT"}, "device_id": "aacca680-7fa2-41e3-996b-c15a56718f9d", "action_type": "SCHEDULE", "description": "Theo thói quen của bạn, đèn phòng ngủ sẽ tự động được bật vào mỗi chiều thứ 2, thứ 3, thứ 5 và thứ 6 lúc 22h. Chúng tôi đã lập lịch cho bạn để đảm bảo không bỏ sót.", "device_name": "Đèn phòng ngủ", "device_slug": "light_bedroom", "explanation": {"threshold": 0.55, "usefulness": true, "cooldown_pass": true, "priority_rank": null, "decision_score": 0.565, "priority_score": null, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "repeated_occurrence"], "cooldown_reasons": [], "cooldown_signature": "TIME_HABIT:light_bedroom:high_weekly_repetition", "usefulness_reasons": ["high_weekly_repetition"], "priority_hard_override": false}, "schedule_payload": {"time": "22:00", "days_of_week": [1, 2, 4, 5], "action_payload": {"power": "ON"}}}	\N	2026-06-07 15:07:25.238895+00
17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	60	SCHEDULE	Tạo lịch bật điều hòa vào buổi tối: Theo thói quen của bạn, điều hòa sẽ tự động được bật vào lúc 23h vào các ngày Chủ nhật, Thứ 3, Thứ 4 và Thứ 7. Chúng tôi đề xuất tạo lịch để đảm bảo điều hòa hoạt động đúng giờ.	{"title": "Tạo lịch bật điều hòa vào buổi tối", "source": {"user_name": "Nguyễn Văn Hùng", "pattern_id": 60, "pattern_type": "TIME_HABIT"}, "device_id": "b29217ff-2b22-4cdb-a25e-828ba5011266", "action_type": "SCHEDULE", "description": "Theo thói quen của bạn, điều hòa sẽ tự động được bật vào lúc 23h vào các ngày Chủ nhật, Thứ 3, Thứ 4 và Thứ 7. Chúng tôi đề xuất tạo lịch để đảm bảo điều hòa hoạt động đúng giờ.", "device_name": "Điều hoà phòng ngủ", "device_slug": "ac_bedroom", "explanation": {"threshold": 0.55, "usefulness": true, "cooldown_pass": true, "priority_rank": null, "decision_score": 0.558, "priority_score": null, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "high_energy_device", "unusual_hour", "repeated_occurrence"], "cooldown_reasons": [], "cooldown_signature": "TIME_HABIT:ac_bedroom:energy_heavy_device,high_weekly_repetition,unusual_hour", "usefulness_reasons": ["energy_heavy_device", "unusual_hour", "high_weekly_repetition"], "priority_hard_override": false}, "schedule_payload": {"time": "23:00", "days_of_week": [0, 2, 3, 6], "action_payload": {"power": "ON"}}}	\N	2026-06-07 15:07:25.238895+00
18	910adcc3-fd19-48e5-8cdc-13e16cf212f7	57	SCHEDULE	Tạo lịch bật quạt phòng ngủ: Theo thói quen của bạn, quạt sẽ tự động bật vào buổi sáng từ Thứ 2 đến Thứ 6 lúc 06:00. Chúng tôi đã lập lịch này để đảm bảo rằng không có sự cố xảy ra.	{"title": "Tạo lịch bật quạt phòng ngủ", "source": {"user_name": "Nguyễn Văn Hùng", "pattern_id": 57, "pattern_type": "TIME_HABIT"}, "device_id": "2df56b5d-2a60-4382-bda8-e150df7805e1", "action_type": "SCHEDULE", "description": "Theo thói quen của bạn, quạt sẽ tự động bật vào buổi sáng từ Thứ 2 đến Thứ 6 lúc 06:00. Chúng tôi đã lập lịch này để đảm bảo rằng không có sự cố xảy ra.", "device_name": "Quạt phòng ngủ", "device_slug": "fan_bedroom", "explanation": {"threshold": 0.55, "usefulness": true, "cooldown_pass": true, "priority_rank": null, "decision_score": 0.558, "priority_score": null, "priority_reason": ["base_type_weight:TIME_HABIT", "pattern_confidence", "repeated_occurrence"], "cooldown_reasons": [], "cooldown_signature": "TIME_HABIT:fan_bedroom:high_weekly_repetition", "usefulness_reasons": ["high_weekly_repetition"], "priority_hard_override": false}, "schedule_payload": {"time": "06:00", "days_of_week": [1, 2, 3, 4, 5], "action_payload": {"power": "ON"}}}	\N	2026-06-07 15:07:25.238895+00
\.


--
-- Data for Name: user_patterns; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_patterns (id, user_id, device_id, pattern_type, pattern_data, confidence, computed_at, is_active, home_id) FROM stdin;
1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 6, "label_vn": "Thường bật lúc 6h", "avg_dur_min": 24.9, "occurrences": 11, "days_of_week": [1, 2, 3, 4, 5]}	1	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
2	910adcc3-fd19-48e5-8cdc-13e16cf212f7	aacca680-7fa2-41e3-996b-c15a56718f9d	TIME_HABIT	{"hour": 22, "label_vn": "Thường bật lúc 22h", "avg_dur_min": 48.9, "occurrences": 10, "days_of_week": [1, 2, 4, 5]}	0.95	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
3	910adcc3-fd19-48e5-8cdc-13e16cf212f7	b29217ff-2b22-4cdb-a25e-828ba5011266	TIME_HABIT	{"hour": 22, "label_vn": "Thường bật lúc 22h", "avg_dur_min": 86.4, "occurrences": 10, "days_of_week": [1, 2, 3, 4, 5]}	0.95	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
4	910adcc3-fd19-48e5-8cdc-13e16cf212f7	2df56b5d-2a60-4382-bda8-e150df7805e1	TIME_HABIT	{"hour": 6, "label_vn": "Thường bật lúc 6h", "avg_dur_min": 37.3, "occurrences": 9, "days_of_week": [1, 2, 3, 4, 5]}	0.86	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
5	910adcc3-fd19-48e5-8cdc-13e16cf212f7	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	TIME_HABIT	{"hour": 18, "label_vn": "Thường bật lúc 18h", "avg_dur_min": 207.2, "occurrences": 9, "days_of_week": [0, 1, 3, 5, 6]}	0.86	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
6	910adcc3-fd19-48e5-8cdc-13e16cf212f7	6cb5a041-7821-4ca8-8c2c-15363bc35047	TIME_HABIT	{"hour": 19, "label_vn": "Thường bật lúc 19h", "avg_dur_min": 144.6, "occurrences": 9, "days_of_week": [0, 4, 6]}	0.86	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
7	910adcc3-fd19-48e5-8cdc-13e16cf212f7	b29217ff-2b22-4cdb-a25e-828ba5011266	TIME_HABIT	{"hour": 23, "label_vn": "Thường bật lúc 23h", "avg_dur_min": 90.2, "occurrences": 8, "days_of_week": [0, 2, 3, 6]}	0.76	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
8	910adcc3-fd19-48e5-8cdc-13e16cf212f7	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	TIME_HABIT	{"hour": 21, "label_vn": "Thường bật lúc 21h", "avg_dur_min": 282.1, "occurrences": 7, "days_of_week": [0, 1, 2, 5, 6]}	0.67	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
9	910adcc3-fd19-48e5-8cdc-13e16cf212f7	6cb5a041-7821-4ca8-8c2c-15363bc35047	TIME_HABIT	{"hour": 20, "label_vn": "Thường bật lúc 20h", "avg_dur_min": 122.3, "occurrences": 6, "days_of_week": [0, 4, 6]}	0.57	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
10	910adcc3-fd19-48e5-8cdc-13e16cf212f7	6cb5a041-7821-4ca8-8c2c-15363bc35047	TIME_HABIT	{"hour": 21, "label_vn": "Thường bật lúc 21h", "avg_dur_min": 285.3, "occurrences": 6, "days_of_week": [0, 1, 5, 6]}	0.57	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
11	910adcc3-fd19-48e5-8cdc-13e16cf212f7	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 8, "label_vn": "Thường bật lúc 8h", "avg_dur_min": 42.0, "occurrences": 6, "days_of_week": [0, 6]}	0.57	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
12	910adcc3-fd19-48e5-8cdc-13e16cf212f7	ef359599-bea0-4f11-8de4-f6c433fbc7fb	TIME_HABIT	{"hour": 18, "label_vn": "Thường bật lúc 18h", "avg_dur_min": 180.5, "occurrences": 6, "days_of_week": [2, 3, 5]}	0.57	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
13	910adcc3-fd19-48e5-8cdc-13e16cf212f7	aacca680-7fa2-41e3-996b-c15a56718f9d	TIME_HABIT	{"hour": 23, "label_vn": "Thường bật lúc 23h", "avg_dur_min": 58.0, "occurrences": 5, "days_of_week": [0, 4, 6]}	0.48	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
14	910adcc3-fd19-48e5-8cdc-13e16cf212f7	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 18, "label_vn": "Thường bật lúc 18h", "avg_dur_min": 39.3, "occurrences": 5, "days_of_week": [1, 2]}	0.48	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
15	910adcc3-fd19-48e5-8cdc-13e16cf212f7	aacca680-7fa2-41e3-996b-c15a56718f9d	TIME_HABIT	{"hour": 5, "label_vn": "Thường bật lúc 5h", "avg_dur_min": 43.2, "occurrences": 4, "days_of_week": [2, 5]}	0.38	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
16	910adcc3-fd19-48e5-8cdc-13e16cf212f7	aacca680-7fa2-41e3-996b-c15a56718f9d	TIME_HABIT	{"hour": 6, "label_vn": "Thường bật lúc 6h", "avg_dur_min": 43.8, "occurrences": 4, "days_of_week": [1, 3, 5]}	0.38	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
17	910adcc3-fd19-48e5-8cdc-13e16cf212f7	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 19, "label_vn": "Thường bật lúc 19h", "avg_dur_min": 48.3, "occurrences": 4, "days_of_week": [4, 5]}	0.38	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
18	910adcc3-fd19-48e5-8cdc-13e16cf212f7	b29217ff-2b22-4cdb-a25e-828ba5011266	TIME_HABIT	{"hour": 19, "label_vn": "Thường bật lúc 19h", "avg_dur_min": 47.8, "occurrences": 4, "days_of_week": [1]}	0.38	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
19	910adcc3-fd19-48e5-8cdc-13e16cf212f7	2df56b5d-2a60-4382-bda8-e150df7805e1	TIME_HABIT	{"hour": 5, "label_vn": "Thường bật lúc 5h", "avg_dur_min": 44.0, "occurrences": 3, "days_of_week": [1, 3, 5]}	0.29	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
20	910adcc3-fd19-48e5-8cdc-13e16cf212f7	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	TIME_HABIT	{"hour": 17, "label_vn": "Thường bật lúc 17h", "avg_dur_min": 176.0, "occurrences": 3, "days_of_week": [2, 3, 5]}	0.29	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
21	910adcc3-fd19-48e5-8cdc-13e16cf212f7	6cb5a041-7821-4ca8-8c2c-15363bc35047	TIME_HABIT	{"hour": 22, "label_vn": "Thường bật lúc 22h", "avg_dur_min": 126.0, "occurrences": 3, "days_of_week": [3, 5]}	0.29	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
22	910adcc3-fd19-48e5-8cdc-13e16cf212f7	ef359599-bea0-4f11-8de4-f6c433fbc7fb	TIME_HABIT	{"hour": 17, "label_vn": "Thường bật lúc 17h", "avg_dur_min": 163.3, "occurrences": 3, "days_of_week": [1, 4, 5]}	0.29	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
23	910adcc3-fd19-48e5-8cdc-13e16cf212f7	ef359599-bea0-4f11-8de4-f6c433fbc7fb	TIME_HABIT	{"hour": 20, "label_vn": "Thường bật lúc 20h", "avg_dur_min": 61.0, "occurrences": 3, "days_of_week": [2, 5]}	0.29	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
54	910adcc3-fd19-48e5-8cdc-13e16cf212f7	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 6, "label_vn": "Thường bật lúc 6h", "avg_dur_min": 24.9, "occurrences": 11, "days_of_week": [1, 2, 3, 4, 5]}	1	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
55	910adcc3-fd19-48e5-8cdc-13e16cf212f7	aacca680-7fa2-41e3-996b-c15a56718f9d	TIME_HABIT	{"hour": 22, "label_vn": "Thường bật lúc 22h", "avg_dur_min": 48.9, "occurrences": 10, "days_of_week": [1, 2, 4, 5]}	0.95	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
56	910adcc3-fd19-48e5-8cdc-13e16cf212f7	b29217ff-2b22-4cdb-a25e-828ba5011266	TIME_HABIT	{"hour": 22, "label_vn": "Thường bật lúc 22h", "avg_dur_min": 86.4, "occurrences": 10, "days_of_week": [1, 2, 3, 4, 5]}	0.95	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
79	910adcc3-fd19-48e5-8cdc-13e16cf212f7	6cb5a041-7821-4ca8-8c2c-15363bc35047	ANOMALY	{"label_vn": "Có thể quên tắt (avg 171.4 phút, vượt ngưỡng 1 lần)", "avg_dur_min": 171.4, "occurrences": 1, "threshold_min": 343.9}	0.2	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
57	910adcc3-fd19-48e5-8cdc-13e16cf212f7	2df56b5d-2a60-4382-bda8-e150df7805e1	TIME_HABIT	{"hour": 6, "label_vn": "Thường bật lúc 6h", "avg_dur_min": 37.3, "occurrences": 9, "days_of_week": [1, 2, 3, 4, 5]}	0.86	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
58	910adcc3-fd19-48e5-8cdc-13e16cf212f7	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	TIME_HABIT	{"hour": 18, "label_vn": "Thường bật lúc 18h", "avg_dur_min": 207.2, "occurrences": 9, "days_of_week": [0, 1, 3, 5, 6]}	0.86	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
59	910adcc3-fd19-48e5-8cdc-13e16cf212f7	6cb5a041-7821-4ca8-8c2c-15363bc35047	TIME_HABIT	{"hour": 19, "label_vn": "Thường bật lúc 19h", "avg_dur_min": 144.6, "occurrences": 9, "days_of_week": [0, 4, 6]}	0.86	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
60	910adcc3-fd19-48e5-8cdc-13e16cf212f7	b29217ff-2b22-4cdb-a25e-828ba5011266	TIME_HABIT	{"hour": 23, "label_vn": "Thường bật lúc 23h", "avg_dur_min": 90.2, "occurrences": 8, "days_of_week": [0, 2, 3, 6]}	0.76	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
61	910adcc3-fd19-48e5-8cdc-13e16cf212f7	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	TIME_HABIT	{"hour": 21, "label_vn": "Thường bật lúc 21h", "avg_dur_min": 282.0, "occurrences": 6, "days_of_week": [0, 1, 2, 5, 6]}	0.57	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
62	910adcc3-fd19-48e5-8cdc-13e16cf212f7	6cb5a041-7821-4ca8-8c2c-15363bc35047	TIME_HABIT	{"hour": 20, "label_vn": "Thường bật lúc 20h", "avg_dur_min": 122.3, "occurrences": 6, "days_of_week": [0, 4, 6]}	0.57	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
63	910adcc3-fd19-48e5-8cdc-13e16cf212f7	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 8, "label_vn": "Thường bật lúc 8h", "avg_dur_min": 42.0, "occurrences": 6, "days_of_week": [0, 6]}	0.57	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
64	910adcc3-fd19-48e5-8cdc-13e16cf212f7	ef359599-bea0-4f11-8de4-f6c433fbc7fb	TIME_HABIT	{"hour": 18, "label_vn": "Thường bật lúc 18h", "avg_dur_min": 180.5, "occurrences": 6, "days_of_week": [2, 3, 5]}	0.57	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
65	910adcc3-fd19-48e5-8cdc-13e16cf212f7	6cb5a041-7821-4ca8-8c2c-15363bc35047	TIME_HABIT	{"hour": 21, "label_vn": "Thường bật lúc 21h", "avg_dur_min": 305.6, "occurrences": 5, "days_of_week": [0, 1, 5, 6]}	0.48	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
66	910adcc3-fd19-48e5-8cdc-13e16cf212f7	aacca680-7fa2-41e3-996b-c15a56718f9d	TIME_HABIT	{"hour": 23, "label_vn": "Thường bật lúc 23h", "avg_dur_min": 58.0, "occurrences": 5, "days_of_week": [0, 4, 6]}	0.48	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
67	910adcc3-fd19-48e5-8cdc-13e16cf212f7	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 18, "label_vn": "Thường bật lúc 18h", "avg_dur_min": 39.3, "occurrences": 5, "days_of_week": [1, 2]}	0.48	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
68	910adcc3-fd19-48e5-8cdc-13e16cf212f7	aacca680-7fa2-41e3-996b-c15a56718f9d	TIME_HABIT	{"hour": 5, "label_vn": "Thường bật lúc 5h", "avg_dur_min": 43.2, "occurrences": 4, "days_of_week": [2, 5]}	0.38	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
69	910adcc3-fd19-48e5-8cdc-13e16cf212f7	aacca680-7fa2-41e3-996b-c15a56718f9d	TIME_HABIT	{"hour": 6, "label_vn": "Thường bật lúc 6h", "avg_dur_min": 43.8, "occurrences": 4, "days_of_week": [1, 3, 5]}	0.38	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
70	910adcc3-fd19-48e5-8cdc-13e16cf212f7	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 19, "label_vn": "Thường bật lúc 19h", "avg_dur_min": 48.3, "occurrences": 4, "days_of_week": [4, 5]}	0.38	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
71	910adcc3-fd19-48e5-8cdc-13e16cf212f7	b29217ff-2b22-4cdb-a25e-828ba5011266	TIME_HABIT	{"hour": 19, "label_vn": "Thường bật lúc 19h", "avg_dur_min": 47.8, "occurrences": 4, "days_of_week": [1]}	0.38	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
72	910adcc3-fd19-48e5-8cdc-13e16cf212f7	2df56b5d-2a60-4382-bda8-e150df7805e1	TIME_HABIT	{"hour": 5, "label_vn": "Thường bật lúc 5h", "avg_dur_min": 44.0, "occurrences": 3, "days_of_week": [1, 3, 5]}	0.29	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
73	910adcc3-fd19-48e5-8cdc-13e16cf212f7	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	TIME_HABIT	{"hour": 17, "label_vn": "Thường bật lúc 17h", "avg_dur_min": 176.0, "occurrences": 3, "days_of_week": [2, 3, 5]}	0.29	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
74	910adcc3-fd19-48e5-8cdc-13e16cf212f7	6cb5a041-7821-4ca8-8c2c-15363bc35047	TIME_HABIT	{"hour": 22, "label_vn": "Thường bật lúc 22h", "avg_dur_min": 126.0, "occurrences": 3, "days_of_week": [3, 5]}	0.29	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
75	910adcc3-fd19-48e5-8cdc-13e16cf212f7	ef359599-bea0-4f11-8de4-f6c433fbc7fb	TIME_HABIT	{"hour": 17, "label_vn": "Thường bật lúc 17h", "avg_dur_min": 163.3, "occurrences": 3, "days_of_week": [1, 4, 5]}	0.29	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
76	910adcc3-fd19-48e5-8cdc-13e16cf212f7	ef359599-bea0-4f11-8de4-f6c433fbc7fb	TIME_HABIT	{"hour": 20, "label_vn": "Thường bật lúc 20h", "avg_dur_min": 61.0, "occurrences": 3, "days_of_week": [2, 5]}	0.29	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
24	910adcc3-fd19-48e5-8cdc-13e16cf212f7	2df56b5d-2a60-4382-bda8-e150df7805e1	ANOMALY	{"label_vn": "Có thể quên tắt (avg 48.8 phút, vượt ngưỡng 1 lần)", "avg_dur_min": 48.8, "occurrences": 1, "threshold_min": 110.0}	0.2	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
25	910adcc3-fd19-48e5-8cdc-13e16cf212f7	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	ANOMALY	{"label_vn": "Có thể quên tắt (avg 230.1 phút, vượt ngưỡng 1 lần)", "avg_dur_min": 230.1, "occurrences": 1, "threshold_min": 373.6}	0.2	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
26	910adcc3-fd19-48e5-8cdc-13e16cf212f7	6cb5a041-7821-4ca8-8c2c-15363bc35047	ANOMALY	{"label_vn": "Có thể quên tắt (avg 171.9 phút, vượt ngưỡng 1 lần)", "avg_dur_min": 171.9, "occurrences": 1, "threshold_min": 340.6}	0.2	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
27	910adcc3-fd19-48e5-8cdc-13e16cf212f7	aacca680-7fa2-41e3-996b-c15a56718f9d	ANOMALY	{"label_vn": "Có thể quên tắt (avg 49.3 phút, vượt ngưỡng 1 lần)", "avg_dur_min": 49.3, "occurrences": 1, "threshold_min": 75.4}	0.2	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
28	910adcc3-fd19-48e5-8cdc-13e16cf212f7	af1dad60-6dbd-4093-88c4-d041f3515c17	ANOMALY	{"label_vn": "Có thể quên tắt (avg 34.6 phút, vượt ngưỡng 1 lần)", "avg_dur_min": 34.6, "occurrences": 1, "threshold_min": 59.0}	0.2	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
77	910adcc3-fd19-48e5-8cdc-13e16cf212f7	2df56b5d-2a60-4382-bda8-e150df7805e1	ANOMALY	{"label_vn": "Có thể quên tắt (avg 48.8 phút, vượt ngưỡng 1 lần)", "avg_dur_min": 48.8, "occurrences": 1, "threshold_min": 110.0}	0.2	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
78	910adcc3-fd19-48e5-8cdc-13e16cf212f7	aacca680-7fa2-41e3-996b-c15a56718f9d	ANOMALY	{"label_vn": "Có thể quên tắt (avg 49.3 phút, vượt ngưỡng 1 lần)", "avg_dur_min": 49.3, "occurrences": 1, "threshold_min": 75.4}	0.2	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
80	910adcc3-fd19-48e5-8cdc-13e16cf212f7	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	ANOMALY	{"label_vn": "Có thể quên tắt (avg 226.9 phút, vượt ngưỡng 1 lần)", "avg_dur_min": 226.9, "occurrences": 1, "threshold_min": 372.4}	0.2	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
81	910adcc3-fd19-48e5-8cdc-13e16cf212f7	af1dad60-6dbd-4093-88c4-d041f3515c17	ANOMALY	{"label_vn": "Có thể quên tắt (avg 34.6 phút, vượt ngưỡng 1 lần)", "avg_dur_min": 34.6, "occurrences": 1, "threshold_min": 59.0}	0.2	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
29	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 11, "label_vn": "Thường bật lúc 11h", "avg_dur_min": 40.9, "occurrences": 20, "days_of_week": [1, 2, 3, 4, 5]}	1	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
30	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	aacca680-7fa2-41e3-996b-c15a56718f9d	TIME_HABIT	{"hour": 14, "label_vn": "Thường bật lúc 14h", "avg_dur_min": 146.3, "occurrences": 11, "days_of_week": [1, 2, 4, 5]}	1	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
31	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	ef359599-bea0-4f11-8de4-f6c433fbc7fb	TIME_HABIT	{"hour": 9, "label_vn": "Thường bật lúc 9h", "avg_dur_min": 284.5, "occurrences": 10, "days_of_week": [0, 1, 2, 3, 6]}	0.95	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
32	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	aacca680-7fa2-41e3-996b-c15a56718f9d	TIME_HABIT	{"hour": 6, "label_vn": "Thường bật lúc 6h", "avg_dur_min": 34.6, "occurrences": 9, "days_of_week": [0, 1, 2, 3, 5, 6]}	0.86	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
33	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	aacca680-7fa2-41e3-996b-c15a56718f9d	TIME_HABIT	{"hour": 22, "label_vn": "Thường bật lúc 22h", "avg_dur_min": 109.7, "occurrences": 8, "days_of_week": [0, 3, 4, 5, 6]}	0.76	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
34	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	ef359599-bea0-4f11-8de4-f6c433fbc7fb	TIME_HABIT	{"hour": 14, "label_vn": "Thường bật lúc 14h", "avg_dur_min": 117.6, "occurrences": 8, "days_of_week": [1, 2, 3, 4, 5]}	0.76	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
35	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	2df56b5d-2a60-4382-bda8-e150df7805e1	TIME_HABIT	{"hour": 21, "label_vn": "Thường bật lúc 21h", "avg_dur_min": 26.0, "occurrences": 7, "days_of_week": [1, 2, 3, 4, 5]}	0.67	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
36	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	aacca680-7fa2-41e3-996b-c15a56718f9d	TIME_HABIT	{"hour": 21, "label_vn": "Thường bật lúc 21h", "avg_dur_min": 30.0, "occurrences": 7, "days_of_week": [1, 2, 3, 4, 5]}	0.67	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
37	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 10, "label_vn": "Thường bật lúc 10h", "avg_dur_min": 20.7, "occurrences": 7, "days_of_week": [1, 2, 3, 4, 5]}	0.67	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
38	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 6, "label_vn": "Thường bật lúc 6h", "avg_dur_min": 42.5, "occurrences": 6, "days_of_week": [1, 2, 3, 5]}	0.57	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
39	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 17, "label_vn": "Thường bật lúc 17h", "avg_dur_min": 58.8, "occurrences": 6, "days_of_week": [1, 4, 5]}	0.57	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
40	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	2df56b5d-2a60-4382-bda8-e150df7805e1	TIME_HABIT	{"hour": 9, "label_vn": "Thường bật lúc 9h", "avg_dur_min": 218.6, "occurrences": 5, "days_of_week": [2, 5]}	0.48	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
41	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	2df56b5d-2a60-4382-bda8-e150df7805e1	TIME_HABIT	{"hour": 13, "label_vn": "Thường bật lúc 13h", "avg_dur_min": 97.2, "occurrences": 5, "days_of_week": [1, 2, 4, 5]}	0.48	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
42	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	TIME_HABIT	{"hour": 8, "label_vn": "Thường bật lúc 8h", "avg_dur_min": 238.3, "occurrences": 5, "days_of_week": [1, 2, 4, 6]}	0.48	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
43	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	aacca680-7fa2-41e3-996b-c15a56718f9d	TIME_HABIT	{"hour": 9, "label_vn": "Thường bật lúc 9h", "avg_dur_min": 249.2, "occurrences": 5, "days_of_week": [2, 5]}	0.48	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
44	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	b29217ff-2b22-4cdb-a25e-828ba5011266	TIME_HABIT	{"hour": 13, "label_vn": "Thường bật lúc 13h", "avg_dur_min": 63.2, "occurrences": 5, "days_of_week": [1, 2, 4, 5]}	0.48	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
45	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	ef359599-bea0-4f11-8de4-f6c433fbc7fb	TIME_HABIT	{"hour": 19, "label_vn": "Thường bật lúc 19h", "avg_dur_min": 93.5, "occurrences": 5, "days_of_week": [2, 3, 4, 5]}	0.48	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
46	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	TIME_HABIT	{"hour": 14, "label_vn": "Thường bật lúc 14h", "avg_dur_min": 120.0, "occurrences": 4, "days_of_week": [1, 3, 5]}	0.38	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
47	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 16, "label_vn": "Thường bật lúc 16h", "avg_dur_min": 54.0, "occurrences": 4, "days_of_week": [2, 3, 5]}	0.38	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
48	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	2df56b5d-2a60-4382-bda8-e150df7805e1	TIME_HABIT	{"hour": 14, "label_vn": "Thường bật lúc 14h", "avg_dur_min": 148.3, "occurrences": 3, "days_of_week": [1, 4]}	0.29	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
49	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	TIME_HABIT	{"hour": 13, "label_vn": "Thường bật lúc 13h", "avg_dur_min": 130.5, "occurrences": 3, "days_of_week": [3, 4]}	0.29	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
50	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 7, "label_vn": "Thường bật lúc 7h", "avg_dur_min": 37.7, "occurrences": 3, "days_of_week": [1, 3, 5]}	0.29	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
51	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	b29217ff-2b22-4cdb-a25e-828ba5011266	TIME_HABIT	{"hour": 22, "label_vn": "Thường bật lúc 22h", "avg_dur_min": 78.0, "occurrences": 3, "days_of_week": [0, 6]}	0.29	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
82	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 11, "label_vn": "Thường bật lúc 11h", "avg_dur_min": 40.9, "occurrences": 20, "days_of_week": [1, 2, 3, 4, 5]}	1	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
83	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	aacca680-7fa2-41e3-996b-c15a56718f9d	TIME_HABIT	{"hour": 14, "label_vn": "Thường bật lúc 14h", "avg_dur_min": 146.3, "occurrences": 11, "days_of_week": [1, 2, 4, 5]}	1	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
84	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	ef359599-bea0-4f11-8de4-f6c433fbc7fb	TIME_HABIT	{"hour": 9, "label_vn": "Thường bật lúc 9h", "avg_dur_min": 284.5, "occurrences": 10, "days_of_week": [0, 1, 2, 3, 6]}	0.95	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
85	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	aacca680-7fa2-41e3-996b-c15a56718f9d	TIME_HABIT	{"hour": 6, "label_vn": "Thường bật lúc 6h", "avg_dur_min": 34.6, "occurrences": 9, "days_of_week": [0, 1, 2, 3, 5, 6]}	0.86	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
86	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	aacca680-7fa2-41e3-996b-c15a56718f9d	TIME_HABIT	{"hour": 22, "label_vn": "Thường bật lúc 22h", "avg_dur_min": 109.7, "occurrences": 8, "days_of_week": [0, 3, 4, 5, 6]}	0.76	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
87	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	2df56b5d-2a60-4382-bda8-e150df7805e1	TIME_HABIT	{"hour": 21, "label_vn": "Thường bật lúc 21h", "avg_dur_min": 26.0, "occurrences": 7, "days_of_week": [1, 2, 3, 4, 5]}	0.67	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
88	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	aacca680-7fa2-41e3-996b-c15a56718f9d	TIME_HABIT	{"hour": 21, "label_vn": "Thường bật lúc 21h", "avg_dur_min": 30.0, "occurrences": 7, "days_of_week": [1, 2, 3, 4, 5]}	0.67	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
89	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 10, "label_vn": "Thường bật lúc 10h", "avg_dur_min": 20.7, "occurrences": 7, "days_of_week": [1, 2, 3, 4, 5]}	0.67	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
90	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	ef359599-bea0-4f11-8de4-f6c433fbc7fb	TIME_HABIT	{"hour": 14, "label_vn": "Thường bật lúc 14h", "avg_dur_min": 115.7, "occurrences": 7, "days_of_week": [1, 2, 3, 4, 5]}	0.67	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
91	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 6, "label_vn": "Thường bật lúc 6h", "avg_dur_min": 42.5, "occurrences": 6, "days_of_week": [1, 2, 3, 5]}	0.57	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
92	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 17, "label_vn": "Thường bật lúc 17h", "avg_dur_min": 58.8, "occurrences": 6, "days_of_week": [1, 4, 5]}	0.57	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
93	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	2df56b5d-2a60-4382-bda8-e150df7805e1	TIME_HABIT	{"hour": 9, "label_vn": "Thường bật lúc 9h", "avg_dur_min": 218.6, "occurrences": 5, "days_of_week": [2, 5]}	0.48	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
94	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	2df56b5d-2a60-4382-bda8-e150df7805e1	TIME_HABIT	{"hour": 13, "label_vn": "Thường bật lúc 13h", "avg_dur_min": 97.2, "occurrences": 5, "days_of_week": [1, 2, 4, 5]}	0.48	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
95	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	TIME_HABIT	{"hour": 8, "label_vn": "Thường bật lúc 8h", "avg_dur_min": 238.3, "occurrences": 5, "days_of_week": [1, 2, 4, 6]}	0.48	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
96	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	aacca680-7fa2-41e3-996b-c15a56718f9d	TIME_HABIT	{"hour": 9, "label_vn": "Thường bật lúc 9h", "avg_dur_min": 249.2, "occurrences": 5, "days_of_week": [2, 5]}	0.48	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
97	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	b29217ff-2b22-4cdb-a25e-828ba5011266	TIME_HABIT	{"hour": 13, "label_vn": "Thường bật lúc 13h", "avg_dur_min": 63.2, "occurrences": 5, "days_of_week": [1, 2, 4, 5]}	0.48	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
98	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	ef359599-bea0-4f11-8de4-f6c433fbc7fb	TIME_HABIT	{"hour": 19, "label_vn": "Thường bật lúc 19h", "avg_dur_min": 93.5, "occurrences": 5, "days_of_week": [2, 3, 4, 5]}	0.48	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
99	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	2df56b5d-2a60-4382-bda8-e150df7805e1	TIME_HABIT	{"hour": 14, "label_vn": "Thường bật lúc 14h", "avg_dur_min": 148.3, "occurrences": 3, "days_of_week": [1, 4]}	0.29	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
100	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	TIME_HABIT	{"hour": 13, "label_vn": "Thường bật lúc 13h", "avg_dur_min": 130.5, "occurrences": 3, "days_of_week": [3, 4]}	0.29	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
101	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	5c3941b6-cf40-4842-bbbc-2d36bbbdee25	TIME_HABIT	{"hour": 14, "label_vn": "Thường bật lúc 14h", "avg_dur_min": 120.0, "occurrences": 3, "days_of_week": [1, 3, 5]}	0.29	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
102	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 7, "label_vn": "Thường bật lúc 7h", "avg_dur_min": 37.7, "occurrences": 3, "days_of_week": [1, 3, 5]}	0.29	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
103	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	af1dad60-6dbd-4093-88c4-d041f3515c17	TIME_HABIT	{"hour": 16, "label_vn": "Thường bật lúc 16h", "avg_dur_min": 62.0, "occurrences": 3, "days_of_week": [2, 3, 5]}	0.29	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
104	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	b29217ff-2b22-4cdb-a25e-828ba5011266	TIME_HABIT	{"hour": 22, "label_vn": "Thường bật lúc 22h", "avg_dur_min": 78.0, "occurrences": 3, "days_of_week": [0, 6]}	0.29	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
52	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	2df56b5d-2a60-4382-bda8-e150df7805e1	ANOMALY	{"label_vn": "Có thể quên tắt (avg 135.8 phút, vượt ngưỡng 1 lần)", "avg_dur_min": 135.8, "occurrences": 1, "threshold_min": 306.1}	0.2	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
53	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	aacca680-7fa2-41e3-996b-c15a56718f9d	ANOMALY	{"label_vn": "Có thể quên tắt (avg 105.8 phút, vượt ngưỡng 1 lần)", "avg_dur_min": 105.8, "occurrences": 1, "threshold_min": 290.3}	0.2	2026-06-07 06:59:08.894319+00	f	3716450c-0d6b-4900-9341-b68b64b44bed
105	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	2df56b5d-2a60-4382-bda8-e150df7805e1	ANOMALY	{"label_vn": "Có thể quên tắt (avg 135.8 phút, vượt ngưỡng 1 lần)", "avg_dur_min": 135.8, "occurrences": 1, "threshold_min": 306.1}	0.2	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
106	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	aacca680-7fa2-41e3-996b-c15a56718f9d	ANOMALY	{"label_vn": "Có thể quên tắt (avg 105.8 phút, vượt ngưỡng 1 lần)", "avg_dur_min": 105.8, "occurrences": 1, "threshold_min": 290.3}	0.2	2026-06-07 15:05:46.281824+00	t	3716450c-0d6b-4900-9341-b68b64b44bed
\.


--
-- Data for Name: user_presence; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_presence (id, user_id, room_id, is_home, detected_by, last_seen, home_id) FROM stdin;
1	910adcc3-fd19-48e5-8cdc-13e16cf212f7	\N	f	APP	2026-06-07 06:58:43.647579+00	3716450c-0d6b-4900-9341-b68b64b44bed
2	8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	\N	f	APP	2026-06-07 06:58:43.647579+00	3716450c-0d6b-4900-9341-b68b64b44bed
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, email, password_hash, full_name, avatar_url, role, face_encoding, is_active, created_at) FROM stdin;
730f5d00-bec1-464e-b794-6d3c9fe75e26	nguyenphananhbao@gmail.com	$2b$12$Vo4xrv8ywdzzVcJbEKvRseIuioW93N4hmz6/RDxoZGZtgY0kvEo6e	anhbao	\N	MEMBER	\N	t	2026-06-07 07:15:55.585069+00
910adcc3-fd19-48e5-8cdc-13e16cf212f7	hung@example.com	$2b$12$ajLrvr0s8b1M6cNCVSxqa.PuCmucFEIIHz7GbAhOfX3Z1HjEUo476	Nguyễn Văn Hùng	\N	ADMIN	\N	t	2026-06-07 06:58:43.647579+00
8d1cf3f5-3402-44b9-8ebf-a306d1bb23eb	mai@example.com	$2b$12$ajLrvr0s8b1M6cNCVSxqa.PuCmucFEIIHz7GbAhOfX3Z1HjEUo476	Trần Thị Mai	\N	MEMBER	\N	t	2026-06-07 06:58:43.647579+00
\.


--
-- Name: activity_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.activity_logs_id_seq', 1416, true);


--
-- Name: home_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.home_users_id_seq', 2, true);


--
-- Name: schedules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.schedules_id_seq', 1, false);


--
-- Name: suggestion_decision_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.suggestion_decision_logs_id_seq', 318, true);


--
-- Name: suggestion_feedback_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.suggestion_feedback_logs_id_seq', 1, false);


--
-- Name: suggestion_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.suggestion_logs_id_seq', 18, true);


--
-- Name: user_patterns_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_patterns_id_seq', 106, true);


--
-- Name: user_presence_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_presence_id_seq', 2, true);


--
-- Name: activity_logs activity_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: auth_sessions auth_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_sessions
    ADD CONSTRAINT auth_sessions_pkey PRIMARY KEY (id);


--
-- Name: auth_sessions auth_sessions_refresh_token_hash_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_sessions
    ADD CONSTRAINT auth_sessions_refresh_token_hash_key UNIQUE (refresh_token_hash);


--
-- Name: automation_actions automation_actions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.automation_actions
    ADD CONSTRAINT automation_actions_pkey PRIMARY KEY (id);


--
-- Name: automation_conditions automation_conditions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.automation_conditions
    ADD CONSTRAINT automation_conditions_pkey PRIMARY KEY (id);


--
-- Name: automations automations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.automations
    ADD CONSTRAINT automations_pkey PRIMARY KEY (id);


--
-- Name: device_logs device_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_logs
    ADD CONSTRAINT device_logs_pkey PRIMARY KEY (id);


--
-- Name: device_states device_states_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_states
    ADD CONSTRAINT device_states_pkey PRIMARY KEY (device_id);


--
-- Name: devices devices_mqtt_topic_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_mqtt_topic_key UNIQUE (mqtt_topic);


--
-- Name: devices devices_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_pkey PRIMARY KEY (id);


--
-- Name: energy_logs energy_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.energy_logs
    ADD CONSTRAINT energy_logs_pkey PRIMARY KEY (id);


--
-- Name: home_users home_users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.home_users
    ADD CONSTRAINT home_users_pkey PRIMARY KEY (id);


--
-- Name: homes homes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.homes
    ADD CONSTRAINT homes_pkey PRIMARY KEY (id);


--
-- Name: password_reset_tokens password_reset_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_pkey PRIMARY KEY (id);


--
-- Name: password_reset_tokens password_reset_tokens_token_hash_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_token_hash_key UNIQUE (token_hash);


--
-- Name: rooms rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_pkey PRIMARY KEY (id);


--
-- Name: schedules schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_pkey PRIMARY KEY (id);


--
-- Name: security_events security_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.security_events
    ADD CONSTRAINT security_events_pkey PRIMARY KEY (id);


--
-- Name: sensor_data sensor_data_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sensor_data
    ADD CONSTRAINT sensor_data_pkey PRIMARY KEY ("time", device_id, metric_type);


--
-- Name: suggestion_decision_logs suggestion_decision_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggestion_decision_logs
    ADD CONSTRAINT suggestion_decision_logs_pkey PRIMARY KEY (id);


--
-- Name: suggestion_feedback_logs suggestion_feedback_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggestion_feedback_logs
    ADD CONSTRAINT suggestion_feedback_logs_pkey PRIMARY KEY (id);


--
-- Name: suggestion_logs suggestion_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggestion_logs
    ADD CONSTRAINT suggestion_logs_pkey PRIMARY KEY (id);


--
-- Name: home_users uq_home_user; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.home_users
    ADD CONSTRAINT uq_home_user UNIQUE (home_id, user_id);


--
-- Name: suggestion_feedback_logs uq_suggestion_feedback_suggestion_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggestion_feedback_logs
    ADD CONSTRAINT uq_suggestion_feedback_suggestion_id UNIQUE (suggestion_id);


--
-- Name: user_patterns user_patterns_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_patterns
    ADD CONSTRAINT user_patterns_pkey PRIMARY KEY (id);


--
-- Name: user_presence user_presence_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_presence
    ADD CONSTRAINT user_presence_pkey PRIMARY KEY (id);


--
-- Name: user_presence user_presence_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_presence
    ADD CONSTRAINT user_presence_user_id_key UNIQUE (user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_activity_logs_home_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_activity_logs_home_id ON public.activity_logs USING btree (home_id);


--
-- Name: ix_activity_logs_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_activity_logs_id ON public.activity_logs USING btree (id);


--
-- Name: ix_activity_logs_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_activity_logs_timestamp ON public.activity_logs USING btree ("timestamp");


--
-- Name: ix_auth_sessions_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_auth_sessions_user_id ON public.auth_sessions USING btree (user_id);


--
-- Name: ix_device_logs_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_device_logs_timestamp ON public.device_logs USING btree ("timestamp");


--
-- Name: ix_devices_slug; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_devices_slug ON public.devices USING btree (slug);


--
-- Name: ix_energy_logs_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_energy_logs_timestamp ON public.energy_logs USING btree ("timestamp");


--
-- Name: ix_home_users_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_home_users_id ON public.home_users USING btree (id);


--
-- Name: ix_password_reset_tokens_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_password_reset_tokens_user_id ON public.password_reset_tokens USING btree (user_id);


--
-- Name: ix_rooms_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_rooms_id ON public.rooms USING btree (id);


--
-- Name: ix_schedules_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_schedules_id ON public.schedules USING btree (id);


--
-- Name: ix_security_events_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_security_events_timestamp ON public.security_events USING btree ("timestamp");


--
-- Name: ix_suggestion_decision_logs_home_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_suggestion_decision_logs_home_id ON public.suggestion_decision_logs USING btree (home_id);


--
-- Name: ix_suggestion_decision_logs_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_suggestion_decision_logs_id ON public.suggestion_decision_logs USING btree (id);


--
-- Name: ix_suggestion_decision_logs_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_suggestion_decision_logs_user_id ON public.suggestion_decision_logs USING btree (user_id);


--
-- Name: ix_suggestion_feedback_logs_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_suggestion_feedback_logs_id ON public.suggestion_feedback_logs USING btree (id);


--
-- Name: ix_suggestion_logs_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_suggestion_logs_id ON public.suggestion_logs USING btree (id);


--
-- Name: ix_user_patterns_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_patterns_id ON public.user_patterns USING btree (id);


--
-- Name: ix_user_presence_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_presence_id ON public.user_presence USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: activity_logs activity_logs_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id);


--
-- Name: activity_logs activity_logs_home_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_home_id_fkey FOREIGN KEY (home_id) REFERENCES public.homes(id);


--
-- Name: activity_logs activity_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: auth_sessions auth_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_sessions
    ADD CONSTRAINT auth_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: automation_actions automation_actions_automation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.automation_actions
    ADD CONSTRAINT automation_actions_automation_id_fkey FOREIGN KEY (automation_id) REFERENCES public.automations(id) ON DELETE CASCADE;


--
-- Name: automation_actions automation_actions_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.automation_actions
    ADD CONSTRAINT automation_actions_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id);


--
-- Name: automation_conditions automation_conditions_automation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.automation_conditions
    ADD CONSTRAINT automation_conditions_automation_id_fkey FOREIGN KEY (automation_id) REFERENCES public.automations(id) ON DELETE CASCADE;


--
-- Name: automations automations_home_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.automations
    ADD CONSTRAINT automations_home_id_fkey FOREIGN KEY (home_id) REFERENCES public.homes(id) ON DELETE CASCADE;


--
-- Name: device_logs device_logs_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_logs
    ADD CONSTRAINT device_logs_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id) ON DELETE CASCADE;


--
-- Name: device_states device_states_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_states
    ADD CONSTRAINT device_states_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id) ON DELETE CASCADE;


--
-- Name: devices devices_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.rooms(id) ON DELETE SET NULL;


--
-- Name: energy_logs energy_logs_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.energy_logs
    ADD CONSTRAINT energy_logs_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id) ON DELETE CASCADE;


--
-- Name: home_users home_users_home_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.home_users
    ADD CONSTRAINT home_users_home_id_fkey FOREIGN KEY (home_id) REFERENCES public.homes(id) ON DELETE CASCADE;


--
-- Name: home_users home_users_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.home_users
    ADD CONSTRAINT home_users_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: password_reset_tokens password_reset_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: rooms rooms_home_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_home_id_fkey FOREIGN KEY (home_id) REFERENCES public.homes(id) ON DELETE CASCADE;


--
-- Name: schedules schedules_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id) ON DELETE CASCADE;


--
-- Name: schedules schedules_source_suggestion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_source_suggestion_id_fkey FOREIGN KEY (source_suggestion_id) REFERENCES public.suggestion_logs(id);


--
-- Name: security_events security_events_home_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.security_events
    ADD CONSTRAINT security_events_home_id_fkey FOREIGN KEY (home_id) REFERENCES public.homes(id) ON DELETE CASCADE;


--
-- Name: sensor_data sensor_data_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sensor_data
    ADD CONSTRAINT sensor_data_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id);


--
-- Name: suggestion_decision_logs suggestion_decision_logs_home_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggestion_decision_logs
    ADD CONSTRAINT suggestion_decision_logs_home_id_fkey FOREIGN KEY (home_id) REFERENCES public.homes(id) ON DELETE CASCADE;


--
-- Name: suggestion_decision_logs suggestion_decision_logs_pattern_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggestion_decision_logs
    ADD CONSTRAINT suggestion_decision_logs_pattern_id_fkey FOREIGN KEY (pattern_id) REFERENCES public.user_patterns(id) ON DELETE CASCADE;


--
-- Name: suggestion_decision_logs suggestion_decision_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggestion_decision_logs
    ADD CONSTRAINT suggestion_decision_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: suggestion_feedback_logs suggestion_feedback_logs_suggestion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggestion_feedback_logs
    ADD CONSTRAINT suggestion_feedback_logs_suggestion_id_fkey FOREIGN KEY (suggestion_id) REFERENCES public.suggestion_logs(id) ON DELETE CASCADE;


--
-- Name: suggestion_feedback_logs suggestion_feedback_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggestion_feedback_logs
    ADD CONSTRAINT suggestion_feedback_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: suggestion_logs suggestion_logs_pattern_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggestion_logs
    ADD CONSTRAINT suggestion_logs_pattern_id_fkey FOREIGN KEY (pattern_id) REFERENCES public.user_patterns(id);


--
-- Name: suggestion_logs suggestion_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggestion_logs
    ADD CONSTRAINT suggestion_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_patterns user_patterns_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_patterns
    ADD CONSTRAINT user_patterns_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id);


--
-- Name: user_patterns user_patterns_home_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_patterns
    ADD CONSTRAINT user_patterns_home_id_fkey FOREIGN KEY (home_id) REFERENCES public.homes(id);


--
-- Name: user_patterns user_patterns_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_patterns
    ADD CONSTRAINT user_patterns_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_presence user_presence_home_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_presence
    ADD CONSTRAINT user_presence_home_id_fkey FOREIGN KEY (home_id) REFERENCES public.homes(id);


--
-- Name: user_presence user_presence_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_presence
    ADD CONSTRAINT user_presence_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.rooms(id);


--
-- Name: user_presence user_presence_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_presence
    ADD CONSTRAINT user_presence_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict lft0csTHglggbChm7ckQiTXj8U35Jr5Al88KJ9XYwC07U0S4Mm1PZGxsDeiqD5q

