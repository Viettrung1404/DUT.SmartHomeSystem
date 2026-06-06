--
-- PostgreSQL database dump
--

\restrict xtKwwQXEt1rheh3zD1FzjC8nOK0Xmnf3PsaXUoutCoiJff2bELBHPbrBDdpreUr

-- Dumped from database version 17.9
-- Dumped by pg_dump version 17.9

-- Started on 2026-05-28 12:05:58

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
-- TOC entry 5 (class 2615 OID 18680)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

--
-- TOC entry 5128 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS '';


--
-- TOC entry 924 (class 1247 OID 18887)
-- Name: actiontype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.actiontype AS ENUM (
    'SCHEDULE',
    'ALERT',
    'AUTOMATION'
);


ALTER TYPE public.actiontype OWNER TO postgres;

--
-- TOC entry 888 (class 1247 OID 18713)
-- Name: devicetype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.devicetype AS ENUM (
    'LIGHT',
    'FAN',
    'AC',
    'SENSOR',
    'CAMERA',
    'LOCK'
);


ALTER TYPE public.devicetype OWNER TO postgres;

--
-- TOC entry 912 (class 1247 OID 18824)
-- Name: eventtype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.eventtype AS ENUM (
    'DEVICE_ON',
    'DEVICE_OFF',
    'FACE_UNLOCK',
    'FORGOT_OFF',
    'SCENE_ON'
);


ALTER TYPE public.eventtype OWNER TO postgres;

--
-- TOC entry 903 (class 1247 OID 18791)
-- Name: metrictype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.metrictype AS ENUM (
    'TEMP',
    'HUMIDITY',
    'POWER_W',
    'VOLTAGE'
);


ALTER TYPE public.metrictype OWNER TO postgres;

--
-- TOC entry 918 (class 1247 OID 18857)
-- Name: patterntype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.patterntype AS ENUM (
    'CLUSTER',
    'TIME_HABIT',
    'CORRELATION',
    'ANOMALY'
);


ALTER TYPE public.patterntype OWNER TO postgres;

--
-- TOC entry 936 (class 1247 OID 18976)
-- Name: suggestionfeedbacktype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.suggestionfeedbacktype AS ENUM (
    'ACCEPT',
    'REJECT',
    'IGNORE'
);


ALTER TYPE public.suggestionfeedbacktype OWNER TO postgres;

--
-- TOC entry 909 (class 1247 OID 18811)
-- Name: triggersource; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.triggersource AS ENUM (
    'USER',
    'SCHEDULE',
    'SENSOR',
    'AUTOMATION',
    'PHYSICAL_ATTRIBUTED',
    'PHYSICAL_UNKNOWN'
);


ALTER TYPE public.triggersource OWNER TO postgres;

--
-- TOC entry 882 (class 1247 OID 18696)
-- Name: userrole; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.userrole AS ENUM (
    'ADMIN',
    'MEMBER',
    'GUEST'
);


ALTER TYPE public.userrole OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 222 (class 1259 OID 18742)
-- Name: activity_logs; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.activity_logs OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 18741)
-- Name: activity_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.activity_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.activity_logs_id_seq OWNER TO postgres;

--
-- TOC entry 5130 (class 0 OID 0)
-- Dependencies: 221
-- Name: activity_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.activity_logs_id_seq OWNED BY public.activity_logs.id;


--
-- TOC entry 217 (class 1259 OID 18681)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- TOC entry 244 (class 1259 OID 19084)
-- Name: auth_sessions; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.auth_sessions OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 19126)
-- Name: automation_actions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.automation_actions (
    id uuid NOT NULL,
    automation_id uuid NOT NULL,
    device_id uuid,
    action character varying NOT NULL,
    value character varying
);


ALTER TABLE public.automation_actions OWNER TO postgres;

--
-- TOC entry 246 (class 1259 OID 19114)
-- Name: automation_conditions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.automation_conditions (
    id uuid NOT NULL,
    automation_id uuid NOT NULL,
    condition_type character varying NOT NULL,
    value character varying NOT NULL
);


ALTER TABLE public.automation_conditions OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 19035)
-- Name: automations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.automations (
    id uuid NOT NULL,
    home_id uuid NOT NULL,
    name character varying NOT NULL,
    enabled boolean NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.automations OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 19047)
-- Name: device_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.device_logs (
    id uuid NOT NULL,
    device_id uuid NOT NULL,
    action character varying NOT NULL,
    value character varying,
    "timestamp" timestamp without time zone NOT NULL
);


ALTER TABLE public.device_logs OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 18762)
-- Name: device_states; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.device_states (
    device_id uuid NOT NULL,
    is_online boolean,
    state jsonb NOT NULL,
    last_updated timestamp with time zone DEFAULT now()
);


ALTER TABLE public.device_states OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 18725)
-- Name: devices; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.devices OWNER TO postgres;

--
-- TOC entry 242 (class 1259 OID 19060)
-- Name: energy_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.energy_logs (
    id uuid NOT NULL,
    device_id uuid NOT NULL,
    power_usage double precision NOT NULL,
    "timestamp" timestamp without time zone NOT NULL
);


ALTER TABLE public.energy_logs OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 18934)
-- Name: home_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.home_users (
    id integer NOT NULL,
    home_id uuid NOT NULL,
    user_id uuid NOT NULL,
    role public.userrole,
    joined_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.home_users OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 18933)
-- Name: home_users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.home_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.home_users_id_seq OWNER TO postgres;

--
-- TOC entry 5131 (class 0 OID 0)
-- Dependencies: 234
-- Name: home_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.home_users_id_seq OWNED BY public.home_users.id;


--
-- TOC entry 233 (class 1259 OID 18927)
-- Name: homes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.homes (
    id uuid NOT NULL,
    name character varying(100) NOT NULL,
    address character varying(255),
    timezone character varying(50),
    is_active boolean,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.homes OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 19099)
-- Name: password_reset_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.password_reset_tokens (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    token_hash character varying NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    used_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL
);


ALTER TABLE public.password_reset_tokens OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 18686)
-- Name: rooms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rooms (
    id uuid NOT NULL,
    name character varying(50) NOT NULL,
    icon character varying(50),
    image_url text,
    created_at timestamp with time zone DEFAULT now(),
    home_id uuid NOT NULL
);


ALTER TABLE public.rooms OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 18776)
-- Name: schedules; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.schedules OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 18775)
-- Name: schedules_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.schedules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.schedules_id_seq OWNER TO postgres;

--
-- TOC entry 5132 (class 0 OID 0)
-- Dependencies: 224
-- Name: schedules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.schedules_id_seq OWNED BY public.schedules.id;


--
-- TOC entry 243 (class 1259 OID 19071)
-- Name: security_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.security_events (
    id uuid NOT NULL,
    home_id uuid NOT NULL,
    event_type character varying NOT NULL,
    severity character varying NOT NULL,
    description character varying NOT NULL,
    "timestamp" timestamp without time zone NOT NULL
);


ALTER TABLE public.security_events OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 18799)
-- Name: sensor_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sensor_data (
    "time" timestamp with time zone DEFAULT now() NOT NULL,
    device_id uuid NOT NULL,
    metric_type public.metrictype NOT NULL,
    value double precision NOT NULL
);


ALTER TABLE public.sensor_data OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 19008)
-- Name: suggestion_decision_logs; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.suggestion_decision_logs OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 19007)
-- Name: suggestion_decision_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.suggestion_decision_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.suggestion_decision_logs_id_seq OWNER TO postgres;

--
-- TOC entry 5133 (class 0 OID 0)
-- Dependencies: 238
-- Name: suggestion_decision_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.suggestion_decision_logs_id_seq OWNED BY public.suggestion_decision_logs.id;


--
-- TOC entry 237 (class 1259 OID 18984)
-- Name: suggestion_feedback_logs; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.suggestion_feedback_logs OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 18983)
-- Name: suggestion_feedback_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.suggestion_feedback_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.suggestion_feedback_logs_id_seq OWNER TO postgres;

--
-- TOC entry 5134 (class 0 OID 0)
-- Dependencies: 236
-- Name: suggestion_feedback_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.suggestion_feedback_logs_id_seq OWNED BY public.suggestion_feedback_logs.id;


--
-- TOC entry 232 (class 1259 OID 18894)
-- Name: suggestion_logs; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.suggestion_logs OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 18893)
-- Name: suggestion_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.suggestion_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.suggestion_logs_id_seq OWNER TO postgres;

--
-- TOC entry 5135 (class 0 OID 0)
-- Dependencies: 231
-- Name: suggestion_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.suggestion_logs_id_seq OWNED BY public.suggestion_logs.id;


--
-- TOC entry 230 (class 1259 OID 18866)
-- Name: user_patterns; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.user_patterns OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 18865)
-- Name: user_patterns_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_patterns_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_patterns_id_seq OWNER TO postgres;

--
-- TOC entry 5136 (class 0 OID 0)
-- Dependencies: 229
-- Name: user_patterns_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_patterns_id_seq OWNED BY public.user_patterns.id;


--
-- TOC entry 228 (class 1259 OID 18836)
-- Name: user_presence; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.user_presence OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 18835)
-- Name: user_presence_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_presence_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_presence_id_seq OWNER TO postgres;

--
-- TOC entry 5137 (class 0 OID 0)
-- Dependencies: 227
-- Name: user_presence_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_presence_id_seq OWNED BY public.user_presence.id;


--
-- TOC entry 219 (class 1259 OID 18703)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 4817 (class 2604 OID 18745)
-- Name: activity_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_logs ALTER COLUMN id SET DEFAULT nextval('public.activity_logs_id_seq'::regclass);


--
-- TOC entry 4829 (class 2604 OID 18937)
-- Name: home_users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.home_users ALTER COLUMN id SET DEFAULT nextval('public.home_users_id_seq'::regclass);


--
-- TOC entry 4820 (class 2604 OID 18779)
-- Name: schedules id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedules ALTER COLUMN id SET DEFAULT nextval('public.schedules_id_seq'::regclass);


--
-- TOC entry 4834 (class 2604 OID 19011)
-- Name: suggestion_decision_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggestion_decision_logs ALTER COLUMN id SET DEFAULT nextval('public.suggestion_decision_logs_id_seq'::regclass);


--
-- TOC entry 4831 (class 2604 OID 18987)
-- Name: suggestion_feedback_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggestion_feedback_logs ALTER COLUMN id SET DEFAULT nextval('public.suggestion_feedback_logs_id_seq'::regclass);


--
-- TOC entry 4826 (class 2604 OID 18897)
-- Name: suggestion_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggestion_logs ALTER COLUMN id SET DEFAULT nextval('public.suggestion_logs_id_seq'::regclass);


--
-- TOC entry 4824 (class 2604 OID 18869)
-- Name: user_patterns id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_patterns ALTER COLUMN id SET DEFAULT nextval('public.user_patterns_id_seq'::regclass);


--
-- TOC entry 4822 (class 2604 OID 18839)
-- Name: user_presence id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_presence ALTER COLUMN id SET DEFAULT nextval('public.user_presence_id_seq'::regclass);


--
-- TOC entry 5097 (class 0 OID 18742)
-- Dependencies: 222
-- Data for Name: activity_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.activity_logs (id, "timestamp", device_id, user_id, event_type, description, session_end, duration_seconds, trigger_source, metadata, home_id) FROM stdin;
\.


--
-- TOC entry 5092 (class 0 OID 18681)
-- Dependencies: 217
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
f1a2b3c4d5e6
\.


--
-- TOC entry 5119 (class 0 OID 19084)
-- Dependencies: 244
-- Data for Name: auth_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_sessions (id, user_id, refresh_token_hash, user_agent, ip_address, created_at, expires_at, last_used_at, revoked_at) FROM stdin;
124b8d40-351a-456c-b315-02275978204c	e59daddf-b561-4b34-9ad8-a87b1d146aa3	56a13f22257425107e6d74ef1c274408954d391a772af09464f70d31adac9bdd	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36	127.0.0.1	2026-05-13 13:57:45.421913+07	2026-05-20 13:57:45.419044+07	\N	\N
bf19ca02-6593-46d1-93a9-d29ed906f96c	e59daddf-b561-4b34-9ad8-a87b1d146aa3		\N	\N	2026-05-13 14:08:46.801423+07	2027-05-10 13:54:16.4217+07	\N	\N
9208073b-6a43-4f19-b461-b5f4ab5adba8	e59daddf-b561-4b34-9ad8-a87b1d146aa3	acec33720bcfd43b56c97a0db460947095019524356d1bd6ef58f9326044c0f3	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36	127.0.0.1	2026-05-13 14:18:06.044484+07	2026-05-20 14:18:06.04396+07	\N	\N
3be78a2a-47fc-4da0-a861-6ca88f4a92be	e59daddf-b561-4b34-9ad8-a87b1d146aa3	908b05fb8ac55c4d606b070df4454c5065f9b4b5f7579e68e85e3d09141e1772	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36	127.0.0.1	2026-05-28 11:34:15.897469+07	2026-06-04 11:34:15.895403+07	\N	\N
\.


--
-- TOC entry 5122 (class 0 OID 19126)
-- Dependencies: 247
-- Data for Name: automation_actions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.automation_actions (id, automation_id, device_id, action, value) FROM stdin;
9914f31b-49f3-41ce-b9d5-12552fdcb894	3f341733-ab8e-49d0-b4c2-f25354c19fd5	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	off
4c74cdc0-820e-4286-9e17-8dfaafd26e3c	3f341733-ab8e-49d0-b4c2-f25354c19fd5	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	off
ac346765-0461-4322-8a01-2def72135f68	7bd26de3-47cb-464f-8ae0-a3cdd8a0ef69	5617507e-4f26-467c-a39a-bbcf4ae37ca0	set_temperature	25
5b014788-f55e-441f-84b7-6e6854690d97	7bd26de3-47cb-464f-8ae0-a3cdd8a0ef69	eb2dc712-7b4f-4c82-acf2-e88fa0352797	toggle	on
5d3b5012-cd82-467c-8794-9ec1072c1132	8906b82e-d571-40bf-a43f-78f6148fb0d6	5b5eaa06-1ecf-4d98-93ca-f383c0155a75	toggle	open
c6b2a6d8-4551-45c3-a993-068359493806	8eb5b62d-defb-47fc-9d75-15d0a32b1b6c	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	off
9558d6e7-e116-4eb6-97d1-6bbfd734ce16	8eb5b62d-defb-47fc-9d75-15d0a32b1b6c	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	off
bdee0550-0112-450c-ad6c-9867b9fdddff	8eb5b62d-defb-47fc-9d75-15d0a32b1b6c	5617507e-4f26-467c-a39a-bbcf4ae37ca0	toggle	off
db4fe753-2d8f-4413-a911-baf3ee1c243b	8eb5b62d-defb-47fc-9d75-15d0a32b1b6c	eb2dc712-7b4f-4c82-acf2-e88fa0352797	toggle	off
94469e5e-5077-472f-8bbc-341fe556b8f0	2d692dcf-2882-4d91-bfcf-067ff188fb57	5617507e-4f26-467c-a39a-bbcf4ae37ca0	set_temperature	26
fe032654-5938-41a3-94bc-30a334a1264d	2d692dcf-2882-4d91-bfcf-067ff188fb57	8000d19f-46ee-4271-80b4-1168d1b1834e	set_brightness	20
b57e1445-1b0f-4bf1-9a20-b5d91f1d3b8d	2d692dcf-2882-4d91-bfcf-067ff188fb57	5b5eaa06-1ecf-4d98-93ca-f383c0155a75	toggle	close
\.


--
-- TOC entry 5121 (class 0 OID 19114)
-- Dependencies: 246
-- Data for Name: automation_conditions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.automation_conditions (id, automation_id, condition_type, value) FROM stdin;
e17d0f83-c01d-44d3-950f-6e17d1ee4f2e	3f341733-ab8e-49d0-b4c2-f25354c19fd5	time	23:00
e21e9b5c-dadc-4eac-9fef-c06a9eda5e6c	7bd26de3-47cb-464f-8ae0-a3cdd8a0ef69	temperature	> 32
b0d9f58d-a19f-45af-a79a-59ff341322dd	8906b82e-d571-40bf-a43f-78f6148fb0d6	time	07:00
52df5b56-c247-4bbb-9ab9-e03db8aac7b6	8eb5b62d-defb-47fc-9d75-15d0a32b1b6c	device_status	lock_activated
fdfb522d-5576-45d4-a08d-d83423a5282c	2d692dcf-2882-4d91-bfcf-067ff188fb57	time	22:30
\.


--
-- TOC entry 5115 (class 0 OID 19035)
-- Dependencies: 240
-- Data for Name: automations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.automations (id, home_id, name, enabled, created_at) FROM stdin;
3f341733-ab8e-49d0-b4c2-f25354c19fd5	6fcf9da4-756a-437b-86d5-cc85e0b238a9	Tắt đèn lúc 23:00	t	2026-05-10 13:54:16.502176
7bd26de3-47cb-464f-8ae0-a3cdd8a0ef69	6fcf9da4-756a-437b-86d5-cc85e0b238a9	Bật điều hòa khi nhiệt độ > 32°C	t	2026-05-10 13:54:16.503759
8906b82e-d571-40bf-a43f-78f6148fb0d6	6fcf9da4-756a-437b-86d5-cc85e0b238a9	Mở rèm lúc 7:00 sáng	t	2026-05-10 13:54:16.50684
8eb5b62d-defb-47fc-9d75-15d0a32b1b6c	6fcf9da4-756a-437b-86d5-cc85e0b238a9	Tắt tất cả khi ra khỏi nhà	f	2026-05-10 13:54:16.508058
2d692dcf-2882-4d91-bfcf-067ff188fb57	6fcf9da4-756a-437b-86d5-cc85e0b238a9	Chế độ ngủ lúc 22:30	t	2026-05-10 13:54:16.509286
\.


--
-- TOC entry 5116 (class 0 OID 19047)
-- Dependencies: 241
-- Data for Name: device_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.device_logs (id, device_id, action, value, "timestamp") FROM stdin;
84b70805-a30c-4929-a461-7ef293955f75	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	on	2026-05-13 13:54:16.456401
d676dd60-e3d8-4e27-83af-207430507805	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	off	2026-05-12 01:54:16.456436
75a39e5c-79bf-4316-a10b-250044bc80a6	8000d19f-46ee-4271-80b4-1168d1b1834e	brightness	75	2026-05-10 13:54:16.456456
4f02e959-4123-4c2a-91e3-6cd73d680c24	8000d19f-46ee-4271-80b4-1168d1b1834e	brightness	100	2026-05-09 01:54:16.456474
9879bf6b-01ea-4a6c-b7d2-2d12718c2cab	8000d19f-46ee-4271-80b4-1168d1b1834e	brightness	50	2026-05-07 13:54:16.456487
b31bfc54-dd8b-4c61-8a08-7937bf07e8cf	8000d19f-46ee-4271-80b4-1168d1b1834e	brightness	75	2026-05-06 01:54:16.4565
a0d20833-dfdb-453b-997e-8e7e7ead8d63	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	on	2026-05-04 13:54:16.456513
5ae6ea01-cb1c-4894-8729-96f439ce9269	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	off	2026-05-03 01:54:16.456527
f252af4f-ef84-48a1-96fb-7e96a816a68b	8000d19f-46ee-4271-80b4-1168d1b1834e	brightness	75	2026-05-01 13:54:16.45654
538e0fca-5c2c-42cb-8688-26d1ba974d39	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	on	2026-04-30 01:54:16.456553
ff2d2f90-02ca-4363-bb0e-31df002e3176	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	on	2026-04-28 13:54:16.456566
26476622-61d2-4eb5-bea2-d845f514cf61	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	off	2026-04-27 01:54:16.456579
84993091-7833-45d2-95ba-7e3ecf821d82	8000d19f-46ee-4271-80b4-1168d1b1834e	brightness	75	2026-04-25 13:54:16.456592
c5232baa-9666-4e8a-a2a3-e36936cffd6f	8000d19f-46ee-4271-80b4-1168d1b1834e	brightness	100	2026-04-24 01:54:16.456603
45a5f9e8-26d5-4cf8-8c04-8709c0a37f1d	8000d19f-46ee-4271-80b4-1168d1b1834e	brightness	50	2026-04-22 13:54:16.456615
e7e412fb-0fea-42d2-8a50-d8f302f9ab2f	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	on	2026-04-21 01:54:16.456628
d4edf0ea-afd0-4be4-bf55-9939dcc4413d	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	off	2026-04-19 13:54:16.45664
9bda3bcd-6108-4559-9349-3d425279a196	8000d19f-46ee-4271-80b4-1168d1b1834e	brightness	75	2026-04-18 01:54:16.456652
6eb737e0-4912-4c8a-9c91-6c4ec49368d9	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	on	2026-04-16 13:54:16.456663
44a09e41-ac18-4034-a483-ed86cb3c29da	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	off	2026-04-15 01:54:16.456677
f6871720-1038-4039-bbbb-d0f5b8b7078d	5617507e-4f26-467c-a39a-bbcf4ae37ca0	toggle	on	2026-05-13 13:54:16.456689
e25a2061-9f28-46ca-bdc4-34a0fdd38e1f	5617507e-4f26-467c-a39a-bbcf4ae37ca0	toggle	off	2026-05-12 01:54:16.456702
443cefae-d8de-46ba-9785-3732693b4142	5617507e-4f26-467c-a39a-bbcf4ae37ca0	brightness	75	2026-05-10 13:54:16.456714
46cc0ef7-475b-477c-a0d6-c3c0f0b00927	5617507e-4f26-467c-a39a-bbcf4ae37ca0	brightness	100	2026-05-09 01:54:16.456728
0464995c-d169-457b-a5a8-4e0118819cc2	5617507e-4f26-467c-a39a-bbcf4ae37ca0	brightness	50	2026-05-07 13:54:16.456739
4b48ccb2-3772-4066-aa2a-d5ccd8484bdb	5617507e-4f26-467c-a39a-bbcf4ae37ca0	brightness	75	2026-05-06 01:54:16.456751
907e8220-3c46-412d-a3cf-d0d2aa3a7569	5617507e-4f26-467c-a39a-bbcf4ae37ca0	toggle	on	2026-05-04 13:54:16.456762
fc422286-14aa-455b-a748-e80d24ee75d8	5617507e-4f26-467c-a39a-bbcf4ae37ca0	toggle	off	2026-05-03 01:54:16.456776
88fa4c4f-c394-422b-aae8-ff68758c8431	5617507e-4f26-467c-a39a-bbcf4ae37ca0	brightness	75	2026-05-01 13:54:16.456787
e901c63d-dddf-4e77-af7d-eb32f692fa24	5617507e-4f26-467c-a39a-bbcf4ae37ca0	toggle	on	2026-04-30 01:54:16.456799
180b148c-a364-49ee-be91-2f752694b1b4	5617507e-4f26-467c-a39a-bbcf4ae37ca0	toggle	on	2026-04-28 13:54:16.456812
f0f5fd49-c4da-4d10-aaaa-bb4de6aa333e	5617507e-4f26-467c-a39a-bbcf4ae37ca0	toggle	off	2026-04-27 01:54:16.456825
b95ce396-88b6-4ea7-91d9-6df92e0f60c8	5617507e-4f26-467c-a39a-bbcf4ae37ca0	brightness	75	2026-04-25 13:54:16.456836
485f9c59-7433-43a8-8c42-f61e763ba43b	5617507e-4f26-467c-a39a-bbcf4ae37ca0	brightness	100	2026-04-24 01:54:16.456848
7c66c831-6b8f-4a4a-91e1-6e17e8d2d51a	5617507e-4f26-467c-a39a-bbcf4ae37ca0	brightness	50	2026-04-22 13:54:16.456861
9998f988-e907-4689-a7ad-578e528a7c4d	5617507e-4f26-467c-a39a-bbcf4ae37ca0	toggle	on	2026-04-21 01:54:16.456872
ea1ab56f-f0bc-4b94-b9f9-3f0b852309df	5617507e-4f26-467c-a39a-bbcf4ae37ca0	toggle	off	2026-04-19 13:54:16.456884
28865eb7-7b53-4b57-b740-6985cbef628f	5617507e-4f26-467c-a39a-bbcf4ae37ca0	brightness	75	2026-04-18 01:54:16.456896
3cbbf018-0bd0-4aa7-a61f-cfca8418746b	5617507e-4f26-467c-a39a-bbcf4ae37ca0	toggle	on	2026-04-16 13:54:16.456907
5a3d177d-051b-4d8d-89a2-2d9c6a3a57b5	5617507e-4f26-467c-a39a-bbcf4ae37ca0	toggle	off	2026-04-15 01:54:16.456919
53673d02-59c8-408e-8350-eb9579233f05	eb2dc712-7b4f-4c82-acf2-e88fa0352797	toggle	on	2026-05-13 13:54:16.456931
5ad3bcba-3b98-4e62-b664-3f96d8db7990	eb2dc712-7b4f-4c82-acf2-e88fa0352797	toggle	off	2026-05-12 01:54:16.456943
76d1d7fa-6969-434a-9026-7c17915ed024	eb2dc712-7b4f-4c82-acf2-e88fa0352797	brightness	75	2026-05-10 13:54:16.456956
c55a0d1e-5122-4072-b2dd-02579a9a68a8	eb2dc712-7b4f-4c82-acf2-e88fa0352797	brightness	100	2026-05-09 01:54:16.456967
32b8c10e-cbe9-455a-8c7f-9c15475e3a1a	eb2dc712-7b4f-4c82-acf2-e88fa0352797	brightness	50	2026-05-07 13:54:16.456979
f031733a-5bd8-43fa-b66e-d4cf2bc22d32	eb2dc712-7b4f-4c82-acf2-e88fa0352797	brightness	75	2026-05-06 01:54:16.45699
e2e84182-d38d-476d-8a56-400cbeedaf26	eb2dc712-7b4f-4c82-acf2-e88fa0352797	toggle	on	2026-05-04 13:54:16.457002
da411417-25f2-4b90-9f8a-991236195f04	eb2dc712-7b4f-4c82-acf2-e88fa0352797	toggle	off	2026-05-03 01:54:16.457014
5640e3dd-9cf9-41a7-a3ea-76166365bfe1	eb2dc712-7b4f-4c82-acf2-e88fa0352797	brightness	75	2026-05-01 13:54:16.457026
15e8ff75-60d8-4067-bde6-fa4b4b27251a	eb2dc712-7b4f-4c82-acf2-e88fa0352797	toggle	on	2026-04-30 01:54:16.457038
abfdbd26-61d2-4759-8fc2-a100747581cc	eb2dc712-7b4f-4c82-acf2-e88fa0352797	toggle	on	2026-04-28 13:54:16.45705
411920c2-71b5-4769-a32a-237402ea670c	eb2dc712-7b4f-4c82-acf2-e88fa0352797	toggle	off	2026-04-27 01:54:16.457062
1b67fe9c-99f2-4e5a-b920-d23106c09171	eb2dc712-7b4f-4c82-acf2-e88fa0352797	brightness	75	2026-04-25 13:54:16.457074
dc8d60b1-914d-4489-8269-28b4566a2439	eb2dc712-7b4f-4c82-acf2-e88fa0352797	brightness	100	2026-04-24 01:54:16.457085
c8f9781d-b8d6-42fe-8804-e9507af60dcb	eb2dc712-7b4f-4c82-acf2-e88fa0352797	brightness	50	2026-04-22 13:54:16.457096
f39f6cb5-dcfa-4e35-9f2b-eeb54d263a72	eb2dc712-7b4f-4c82-acf2-e88fa0352797	toggle	on	2026-04-21 01:54:16.457107
8fe9f9d9-4eec-4ace-bbc9-1781ecb63074	eb2dc712-7b4f-4c82-acf2-e88fa0352797	toggle	off	2026-04-19 13:54:16.457119
3969e585-4054-48fa-8e88-4c15dc834af6	eb2dc712-7b4f-4c82-acf2-e88fa0352797	brightness	75	2026-04-18 01:54:16.45713
3ef8cc9c-85ad-4e3f-9403-b354b44b05e6	eb2dc712-7b4f-4c82-acf2-e88fa0352797	toggle	on	2026-04-16 13:54:16.457143
513e5ed1-1c87-4533-a624-8965ed0e9fa7	eb2dc712-7b4f-4c82-acf2-e88fa0352797	toggle	off	2026-04-15 01:54:16.457154
c2a69671-698b-4c9a-aa31-1c85a403fa6d	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	on	2026-05-13 13:54:16.457166
42e07b09-dd7c-49f2-9052-f53ca13f03c0	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	off	2026-05-12 01:54:16.457183
121d3aad-2d86-4d5e-b19a-af5d083d776d	d107b36e-9576-4ab4-877e-8facd4dd2a29	brightness	75	2026-05-10 13:54:16.457194
b2ec02db-b138-4d38-b4bd-7c5cbe9dac70	d107b36e-9576-4ab4-877e-8facd4dd2a29	brightness	100	2026-05-09 01:54:16.457206
ca73f959-0c2e-431c-9680-73f66c8b9cd8	d107b36e-9576-4ab4-877e-8facd4dd2a29	brightness	50	2026-05-07 13:54:16.457217
86f9fe00-091e-40cc-aa70-d14229c5f626	d107b36e-9576-4ab4-877e-8facd4dd2a29	brightness	75	2026-05-06 01:54:16.457229
d37f6bfb-0547-494d-aa2f-3cd31f35cd6e	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	on	2026-05-04 13:54:16.457242
9b1a5493-2b35-4ed5-87c3-2b35d148813f	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	off	2026-05-03 01:54:16.457253
d139b5ec-b130-494c-97fb-9c89ff3420cf	d107b36e-9576-4ab4-877e-8facd4dd2a29	brightness	75	2026-05-01 13:54:16.457264
68c92175-bcf5-4437-b91e-602bcfb064f6	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	on	2026-04-30 01:54:16.457275
d062c194-8689-4b5e-95c8-019ce510292d	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	on	2026-04-28 13:54:16.457287
d99c26ad-191e-4dfb-a33c-aa1296b69b06	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	off	2026-04-27 01:54:16.457298
52f23605-8d6e-409c-80dd-cb8b6ee16c1a	d107b36e-9576-4ab4-877e-8facd4dd2a29	brightness	75	2026-04-25 13:54:16.45731
26a4562f-0588-4349-9173-54f45f9e03cc	d107b36e-9576-4ab4-877e-8facd4dd2a29	brightness	100	2026-04-24 01:54:16.457321
5edd3c29-b23c-4f57-a318-800707973546	d107b36e-9576-4ab4-877e-8facd4dd2a29	brightness	50	2026-04-22 13:54:16.457333
0eb38715-c470-4f5b-ad54-5fdaf59faea1	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	on	2026-04-21 01:54:16.457344
64bbc2f6-f60c-46c0-b924-eb8aca281f78	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	off	2026-04-19 13:54:16.457356
adaeb5ca-45ab-48d4-b586-3a8a186c184b	d107b36e-9576-4ab4-877e-8facd4dd2a29	brightness	75	2026-04-18 01:54:16.457367
02594b54-f8dc-4785-a736-78fa9537b28d	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	on	2026-04-16 13:54:16.457379
097ca125-76c9-4a2d-a5e1-3999adc69c66	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	off	2026-04-15 01:54:16.457393
134a04f9-89dd-4809-b4a3-1357856657ca	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	toggle	on	2026-05-13 13:54:16.457405
c895638b-cecd-40c6-9f61-d0ab62a2aadd	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	toggle	off	2026-05-12 01:54:16.457417
38b7cdba-8578-4086-96c6-7ccf2e4d3509	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	brightness	75	2026-05-10 13:54:16.45743
ead4d95b-5ff0-40ce-bfa9-a9d03935debd	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	brightness	100	2026-05-09 01:54:16.457441
002d05c3-77d7-4189-a167-5b33b0aac0c3	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	brightness	50	2026-05-07 13:54:16.457452
a3017188-9bce-43ce-ae4a-d42835b1d36f	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	brightness	75	2026-05-06 01:54:16.457466
a986d345-3dee-48ae-937c-08a4c590a09b	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	toggle	on	2026-05-04 13:54:16.457477
9d02e799-fb76-446f-9d13-1cedc2475777	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	toggle	off	2026-05-03 01:54:16.45749
3e673d96-daf8-4ca3-be34-0655f52a1741	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	brightness	75	2026-05-01 13:54:16.457501
f9691741-d5e4-47d6-aa05-8e16bffa01e9	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	toggle	on	2026-04-30 01:54:16.457512
11fc2827-17c2-44e4-9472-21c9486ccb61	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	toggle	on	2026-04-28 13:54:16.457524
7c95ef10-97bf-4e07-93a7-c93d60446b68	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	toggle	off	2026-04-27 01:54:16.457535
d283ee4c-ca95-4772-8f8d-ce88facdfb77	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	brightness	75	2026-04-25 13:54:16.457547
33e3132e-2826-405f-9433-57f2bf30ca7e	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	brightness	100	2026-04-24 01:54:16.457558
83c3b370-80fd-4af0-aad3-9bb60ece6713	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	brightness	50	2026-04-22 13:54:16.457569
96969a00-4293-4333-bd4b-558c3fbf4954	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	toggle	on	2026-04-21 01:54:16.45758
e1b7ab0f-cc97-42c4-8e68-20b6a8c7c992	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	toggle	off	2026-04-19 13:54:16.457592
5aab3dd1-2be2-4315-bb93-8db3fc3fe010	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	brightness	75	2026-04-18 01:54:16.457603
9066372d-902c-44e2-9203-2c734bbf0eef	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	toggle	on	2026-04-16 13:54:16.457616
3049a317-8687-4590-be62-ad81d4cf1da3	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	toggle	off	2026-04-15 01:54:16.457628
b872ad08-ff1b-4101-a32d-5f32cd420d59	d578ad21-d98c-414a-b66a-df86446d4886	toggle	on	2026-05-13 13:54:16.457641
356c7d39-8b71-4ad1-b642-9b0f9efa7618	d578ad21-d98c-414a-b66a-df86446d4886	toggle	off	2026-05-12 01:54:16.457653
df4f94f9-4ac8-4343-a1bb-72303de9d1d3	d578ad21-d98c-414a-b66a-df86446d4886	brightness	75	2026-05-10 13:54:16.457664
84a59d1f-4bb4-4868-8a28-1a9cbbe97fed	d578ad21-d98c-414a-b66a-df86446d4886	brightness	100	2026-05-09 01:54:16.457677
3499cd05-c7c3-4a5f-a03e-3fe49e3ed10a	d578ad21-d98c-414a-b66a-df86446d4886	brightness	50	2026-05-07 13:54:16.457688
2f9c677b-3003-4055-88ff-06c8ef033d45	d578ad21-d98c-414a-b66a-df86446d4886	brightness	75	2026-05-06 01:54:16.4577
d2d43b2c-7b49-4f4a-9c95-1472fbd64929	d578ad21-d98c-414a-b66a-df86446d4886	toggle	on	2026-05-04 13:54:16.457711
dcb1ef7b-dfda-4194-97d1-7d78135b15d1	d578ad21-d98c-414a-b66a-df86446d4886	toggle	off	2026-05-03 01:54:16.457723
b0f214cf-ba59-4c1b-8a86-057a51f74d7a	d578ad21-d98c-414a-b66a-df86446d4886	brightness	75	2026-05-01 13:54:16.457734
37630adc-78f6-44d5-9a93-f15f6c8853cb	d578ad21-d98c-414a-b66a-df86446d4886	toggle	on	2026-04-30 01:54:16.457746
491b04d2-bd53-4632-9f65-06e1f9fc86a4	d578ad21-d98c-414a-b66a-df86446d4886	toggle	on	2026-04-28 13:54:16.457758
833d33fd-c8c0-4ef2-84de-552992e05c74	d578ad21-d98c-414a-b66a-df86446d4886	toggle	off	2026-04-27 01:54:16.457769
443e25a9-7a42-4d2f-9b9e-46ca0ef6058a	d578ad21-d98c-414a-b66a-df86446d4886	brightness	75	2026-04-25 13:54:16.45778
4730861b-932a-4488-8724-cd3ef618a2c3	d578ad21-d98c-414a-b66a-df86446d4886	brightness	100	2026-04-24 01:54:16.457791
d22528f6-88a3-4a30-b464-f1b5a5962885	d578ad21-d98c-414a-b66a-df86446d4886	brightness	50	2026-04-22 13:54:16.457804
3caa3e9a-8ee3-4dc2-a8dc-6c5b225aadae	d578ad21-d98c-414a-b66a-df86446d4886	toggle	on	2026-04-21 01:54:16.457816
2672f9a7-0ca8-4b5a-9b73-f3326515eba2	d578ad21-d98c-414a-b66a-df86446d4886	toggle	off	2026-04-19 13:54:16.457827
3d2c3252-79e9-48e0-b6f7-7b9213ffb71b	d578ad21-d98c-414a-b66a-df86446d4886	brightness	75	2026-04-18 01:54:16.457839
30991748-11f5-4b24-8774-169f3b42590c	d578ad21-d98c-414a-b66a-df86446d4886	toggle	on	2026-04-16 13:54:16.45785
9ef6c762-cdfd-4fc9-84e1-e89cd4d1ae22	d578ad21-d98c-414a-b66a-df86446d4886	toggle	off	2026-04-15 01:54:16.457861
a389d4f4-61de-410a-919f-8f73854d39a0	e72633f1-87d7-43a8-bc1e-aaaab303c575	toggle	on	2026-05-13 13:54:16.457872
2753a316-ec06-4937-b26e-a283037d3ada	e72633f1-87d7-43a8-bc1e-aaaab303c575	toggle	off	2026-05-12 01:54:16.457883
fb402dfd-2aaf-4832-9a3c-02956ac9dc42	e72633f1-87d7-43a8-bc1e-aaaab303c575	brightness	75	2026-05-10 13:54:16.457895
a2c5219d-437d-41c9-850e-7f8b8709247d	e72633f1-87d7-43a8-bc1e-aaaab303c575	brightness	100	2026-05-09 01:54:16.457906
2c7ea44e-5442-4420-bc24-1f9a9f528a17	e72633f1-87d7-43a8-bc1e-aaaab303c575	brightness	50	2026-05-07 13:54:16.457916
0901bc7b-a9f2-4717-b7e5-af8e6fdec68e	e72633f1-87d7-43a8-bc1e-aaaab303c575	brightness	75	2026-05-06 01:54:16.457928
5c28f10f-87db-47fe-b9a5-60f7ca16574e	e72633f1-87d7-43a8-bc1e-aaaab303c575	toggle	on	2026-05-04 13:54:16.45794
e9ad36b4-898b-4f91-9e8d-1bea8024c9f7	e72633f1-87d7-43a8-bc1e-aaaab303c575	toggle	off	2026-05-03 01:54:16.457951
aef6bf3f-94cc-43e3-bcb6-40e58959e093	e72633f1-87d7-43a8-bc1e-aaaab303c575	brightness	75	2026-05-01 13:54:16.457962
bb1d4529-f369-4c3a-8842-ecfbcb8e386a	e72633f1-87d7-43a8-bc1e-aaaab303c575	toggle	on	2026-04-30 01:54:16.457975
ea29d0ad-8b4b-4b02-bec6-1b2a3ee93dd7	e72633f1-87d7-43a8-bc1e-aaaab303c575	toggle	on	2026-04-28 13:54:16.458071
c5e65ed4-39f1-4837-9c2f-3744e2d8fbfd	e72633f1-87d7-43a8-bc1e-aaaab303c575	toggle	off	2026-04-27 01:54:16.458088
2099e9e8-1cc6-4490-abef-ad1c3c281783	e72633f1-87d7-43a8-bc1e-aaaab303c575	brightness	75	2026-04-25 13:54:16.458102
4b3046bc-17ae-44af-9f21-ecf6ea797f40	e72633f1-87d7-43a8-bc1e-aaaab303c575	brightness	100	2026-04-24 01:54:16.458114
60175ee4-2d8c-4c11-ab60-a69f136ad87a	e72633f1-87d7-43a8-bc1e-aaaab303c575	brightness	50	2026-04-22 13:54:16.458125
a0091e81-cdd3-46f5-9a36-8fe83092e999	e72633f1-87d7-43a8-bc1e-aaaab303c575	toggle	on	2026-04-21 01:54:16.458136
3055908c-ed73-490c-aba9-6fdf505c0e3a	e72633f1-87d7-43a8-bc1e-aaaab303c575	toggle	off	2026-04-19 13:54:16.458149
6ba87899-9187-4958-8569-e9ff3ec9744c	e72633f1-87d7-43a8-bc1e-aaaab303c575	brightness	75	2026-04-18 01:54:16.45816
b8adf38c-4032-422e-80cd-aab28e6fb396	e72633f1-87d7-43a8-bc1e-aaaab303c575	toggle	on	2026-04-16 13:54:16.458173
0136a0a8-cea7-4755-9c7a-5baa1f8722b9	e72633f1-87d7-43a8-bc1e-aaaab303c575	toggle	off	2026-04-15 01:54:16.458185
7c025177-51ad-46b4-86b8-3443f3ba8df3	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	False	2026-05-13 14:21:07.755236
093f848f-75ca-4411-b15f-3d639f6f6f20	b149da7d-abf5-4931-9ef3-3f716e99a982	toggle	False	2026-05-13 14:21:07.798342
e96bbeb5-4620-4676-978e-07d805c41f0e	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	False	2026-05-13 14:21:07.807545
e67ab47a-f7b0-45bf-b860-8bdea08465e2	d578ad21-d98c-414a-b66a-df86446d4886	toggle	False	2026-05-13 14:21:07.817895
6285626f-8097-4d54-8893-448686d0465f	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	False	2026-05-13 14:21:09.558456
8664dd77-1f20-4ca2-860d-74b815838d01	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	False	2026-05-13 14:21:09.563446
0a7cc09e-a23e-49c7-b5ff-bf5644261650	d578ad21-d98c-414a-b66a-df86446d4886	toggle	False	2026-05-13 14:21:09.569186
d552d4a0-363a-4d34-8e07-497f6adf4356	b149da7d-abf5-4931-9ef3-3f716e99a982	toggle	False	2026-05-13 14:21:09.574238
df934365-9ac2-4b05-b6fd-4b611694c2c1	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	False	2026-05-13 14:21:10.189454
2f0a76ae-5339-46f7-9e84-56b799460ae3	b149da7d-abf5-4931-9ef3-3f716e99a982	toggle	False	2026-05-13 14:21:10.194963
b71c5149-2633-44d2-8bc7-7344a17ab8f3	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	False	2026-05-13 14:21:10.199941
b2733729-eb86-426a-9953-2109bbc161d9	d578ad21-d98c-414a-b66a-df86446d4886	toggle	False	2026-05-13 14:21:10.204602
db40af23-80bf-43f3-9d07-51faec48c18a	5617507e-4f26-467c-a39a-bbcf4ae37ca0	toggle	False	2026-05-13 14:21:17.415615
c6895407-8769-4fb2-a323-be4d9de0f924	5617507e-4f26-467c-a39a-bbcf4ae37ca0	toggle	True	2026-05-13 14:21:22.005671
0da763a6-322d-451d-9f3a-1e359ce43456	097527ff-2aed-4d01-94ce-1642f36abee2	toggle	True	2026-05-13 14:21:24.55168
34038f6e-963f-4b55-b47a-ea9790e66ae0	097527ff-2aed-4d01-94ce-1642f36abee2	toggle	False	2026-05-13 14:21:24.830008
00a4e2f8-3918-48f1-b4df-614491271c9e	097527ff-2aed-4d01-94ce-1642f36abee2	toggle	True	2026-05-13 14:21:25.477345
3d884fee-e55b-4db0-a98a-6932c8ed3df6	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	True	2026-05-28 11:34:25.208111
051856ac-3b2f-4e3b-a7c3-156a3699d9ac	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	False	2026-05-28 11:34:27.087272
d71b71e7-02bf-4aeb-aacd-0ece8d8af44a	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	True	2026-05-28 11:34:28.1419
e62e4794-a332-444b-8e3e-e9704891cc3e	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	False	2026-05-28 11:34:28.831627
741d70bb-7dc5-48a2-89e6-b85e1f026fef	d578ad21-d98c-414a-b66a-df86446d4886	toggle	True	2026-05-28 11:34:57.465413
24dbca32-27c8-41f1-9ed8-efad923cb408	d578ad21-d98c-414a-b66a-df86446d4886	toggle	False	2026-05-28 11:34:59.094478
f78af8d9-c96a-4fdf-a7d1-fa733f263379	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	True	2026-05-28 11:35:02.03148
2da46679-d656-4d83-ae5e-9914ddb3fa87	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	False	2026-05-28 11:35:03.999029
bbe5a096-b451-4edf-acf2-7bc9c2aab714	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	True	2026-05-28 11:35:24.845977
81f61439-32cb-4c3d-bbf3-0e8fd98cf0aa	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	False	2026-05-28 11:35:26.278114
9f794a7c-32ac-41c9-9948-ba812d6fb4e2	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	True	2026-05-28 11:35:30.860411
06779fde-3202-4c93-b207-9a283f9cde8c	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	False	2026-05-28 11:35:32.772464
4c3981bf-76d5-4d2f-8563-24b016bbed9c	eb2dc712-7b4f-4c82-acf2-e88fa0352797	toggle	False	2026-05-28 11:36:23.783901
1ad1faf0-8c50-4456-bafe-919d00a76d20	eb2dc712-7b4f-4c82-acf2-e88fa0352797	toggle	True	2026-05-28 11:36:24.725698
31287e72-d5b8-4342-a851-b28872984168	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	True	2026-05-28 11:36:25.926797
51f2e8fa-f484-4db0-8965-6a0f8df1b492	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	False	2026-05-28 11:36:26.413773
75ebbf3c-a767-460f-a8bd-56ec25ba1a71	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	True	2026-05-28 11:36:31.990096
574967b0-3324-4a76-b887-dcda2ce3ab74	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	False	2026-05-28 11:36:33.542159
90a392db-61b3-405d-bb56-dfed2ed6d151	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	True	2026-05-28 11:36:34.119022
44fccbfb-3a28-4fab-8bf7-8c3b851b19ee	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	False	2026-05-28 11:36:34.454261
8b1cfb0b-3fbd-4fc5-ae50-7f211059296a	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	True	2026-05-28 11:36:44.039196
c5e0b459-4152-48cc-8a79-efbcd220570d	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	False	2026-05-28 11:37:22.588713
bb855404-3440-4f9f-9cbe-8f1384e25a69	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	True	2026-05-28 11:57:50.513626
4a4641ab-a496-469e-87c0-9caa45955571	8000d19f-46ee-4271-80b4-1168d1b1834e	toggle	False	2026-05-28 11:57:54.43851
c7bfac1f-cdfd-41fb-810d-25521ab1ec51	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	True	2026-05-28 11:57:58.233248
8151cd0c-8829-4525-aa8a-08ae5543baa2	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	False	2026-05-28 11:57:59.838967
a3d5c141-4c98-4a12-bd68-48c4efe0ef13	b149da7d-abf5-4931-9ef3-3f716e99a982	toggle	True	2026-05-28 11:58:13.225321
1af69ec4-1117-47af-9072-3bf4a0619662	b149da7d-abf5-4931-9ef3-3f716e99a982	toggle	False	2026-05-28 11:58:13.935386
450f5906-b4a6-4d68-81a6-9a767ba5f875	d107b36e-9576-4ab4-877e-8facd4dd2a29	toggle	True	2026-05-28 12:02:29.509613
\.


--
-- TOC entry 5098 (class 0 OID 18762)
-- Dependencies: 223
-- Data for Name: device_states; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.device_states (device_id, is_online, state, last_updated) FROM stdin;
5b5eaa06-1ecf-4d98-93ca-f383c0155a75	t	{"power": "OFF", "position": 100}	2026-05-12 13:54:16.440857+07
44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	t	{"mode": "cool", "power": "OFF", "fanSpeed": "high", "targetTemp": 26, "temperature": 28}	2026-05-12 13:54:16.440857+07
065dcd9c-7b1e-40f8-a1f0-ff1301dd9d3a	t	{"power": "ON", "motion": false, "battery": 92}	2026-05-12 13:54:16.440857+07
cab3a9f4-3ae5-4756-bfd0-4495954dcf2d	t	{"power": "ON", "recording": true, "resolution": "4K"}	2026-05-12 13:54:16.440857+07
9cc4a587-e51d-42c4-9e17-9c00f461e89c	t	{"power": "ON", "battery": 78, "gasLevel": 0}	2026-05-12 13:54:16.440857+07
3a9b486f-8cb0-4cdd-b992-dfb36029b89a	f	{"power": "OFF", "brightness": 100}	2026-05-13 11:54:16.440883+07
e3896e00-1c28-4d8b-98ae-17f4bb501e4f	t	{"power": "OFF", "speed": 1}	2026-05-12 13:54:16.440857+07
6a5531f5-64f4-4398-a5c4-3ae46f08375f	t	{"power": "OFF", "speed": 2}	2026-05-12 13:54:16.440857+07
e72633f1-87d7-43a8-bc1e-aaaab303c575	t	{"power": "OFF", "brightness": 60, "color_temp": 3000}	2026-05-12 13:54:16.440857+07
c966ee3a-02cb-4732-96da-2554b55f8535	t	{"mode": "cool", "power": "ON", "fanSpeed": "low", "targetTemp": 24, "temperature": 27}	2026-05-12 13:54:16.440857+07
91dbf2f8-0008-44fe-9737-96e527ffa930	t	{"power": "ON", "brightness": 50}	2026-05-12 13:54:16.440857+07
1ec52558-ddf2-465d-adf9-ce35a9c55fc4	t	{"power": "OFF", "battery": 65, "isLocked": false}	2026-05-12 13:54:16.440857+07
ae384afc-80fa-4596-a9f5-54c514d7164e	t	{"power": "ON", "recording": true, "resolution": "1080p"}	2026-05-12 13:54:16.440857+07
8000d19f-46ee-4271-80b4-1168d1b1834e	t	{"power": "OFF", "brightness": 75, "color_temp": 4000}	2026-05-28 11:57:54.438206+07
b149da7d-abf5-4931-9ef3-3f716e99a982	t	{"color": "#ff9500", "power": "OFF", "brightness": 20}	2026-05-28 11:58:13.935029+07
d107b36e-9576-4ab4-877e-8facd4dd2a29	t	{"power": "ON", "brightness": 100}	2026-05-28 12:02:29.509318+07
d578ad21-d98c-414a-b66a-df86446d4886	t	{"power": "OFF", "brightness": 90}	2026-05-28 11:34:59.094258+07
097527ff-2aed-4d01-94ce-1642f36abee2	t	{"power": "ON", "battery": 87, "isLocked": true}	2026-05-13 14:21:25.477031+07
5617507e-4f26-467c-a39a-bbcf4ae37ca0	t	{"mode": "cool", "power": "ON", "fanSpeed": "auto", "targetTemp": "25", "temperature": 26}	2026-05-28 12:05:50.651194+07
eb2dc712-7b4f-4c82-acf2-e88fa0352797	t	{"power": "ON", "speed": 3}	2026-05-28 12:05:50.651194+07
\.


--
-- TOC entry 5095 (class 0 OID 18725)
-- Dependencies: 220
-- Data for Name: devices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.devices (id, slug, room_id, name, type, mqtt_topic, config, created_at) FROM stdin;
8000d19f-46ee-4271-80b4-1168d1b1834e	en_led_phong_ngu	e84c36cc-eb12-46c2-8d08-d10203de6793	Đèn LED phòng ngủ	LIGHT	home/en_led_phong_ngu	{}	2026-05-11 21:54:16.440968+07
5617507e-4f26-467c-a39a-bbcf4ae37ca0	ieu_hoa_panasonic	e84c36cc-eb12-46c2-8d08-d10203de6793	Điều hòa Panasonic	AC	home/ieu_hoa_panasonic	{}	2026-05-11 21:54:16.44304+07
eb2dc712-7b4f-4c82-acf2-e88fa0352797	quat_tran_assa	e84c36cc-eb12-46c2-8d08-d10203de6793	Quạt trần ASSA	FAN	home/quat_tran_assa	{}	2026-05-11 21:54:16.444894+07
5b5eaa06-1ecf-4d98-93ca-f383c0155a75	rem_thong_minh	e84c36cc-eb12-46c2-8d08-d10203de6793	Rèm thông minh	LOCK	home/rem_thong_minh	{}	2026-05-11 21:54:16.446643+07
d107b36e-9576-4ab4-877e-8facd4dd2a29	en_tran_phong_khach	b9a3082e-2497-49f7-bd43-e7a729705f18	Đèn trần phòng khách	LIGHT	home/en_tran_phong_khach	{}	2026-05-11 21:54:16.447358+07
44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	ieu_hoa_lg_dual_cool	b9a3082e-2497-49f7-bd43-e7a729705f18	Điều hòa LG Dual Cool	AC	home/ieu_hoa_lg_dual_cool	{}	2026-05-11 21:54:16.448017+07
cab3a9f4-3ae5-4756-bfd0-4495954dcf2d	camera_an_ninh_4k	b9a3082e-2497-49f7-bd43-e7a729705f18	Camera an ninh 4K	CAMERA	home/camera_an_ninh_4k	{}	2026-05-11 21:54:16.449235+07
d578ad21-d98c-414a-b66a-df86446d4886	en_bep	95d1fdcc-75c7-4155-b1b2-2c877bcce770	Đèn bếp	LIGHT	home/en_bep	{}	2026-05-11 21:54:16.449955+07
9cc4a587-e51d-42c4-9e17-9c00f461e89c	cam_bien_khi_gas	95d1fdcc-75c7-4155-b1b2-2c877bcce770	Cảm biến khí gas	SENSOR	home/cam_bien_khi_gas	{}	2026-05-11 21:54:16.450586+07
3a9b486f-8cb0-4cdd-b992-dfb36029b89a	en_nha_tam	81922cb9-60a4-4c70-abb8-55ff18e95097	Đèn nhà tắm	LIGHT	home/en_nha_tam	{}	2026-05-11 21:54:16.45119+07
b149da7d-abf5-4931-9ef3-3f716e99a982	en_ngu_night_light	5f51de5c-b912-4cd5-bd6c-965da8fd021f	Đèn ngủ Night Light	LIGHT	home/en_ngu_night_light	{}	2026-05-11 21:54:16.452382+07
6a5531f5-64f4-4398-a5c4-3ae46f08375f	quat_ung_xiaomi	5f51de5c-b912-4cd5-bd6c-965da8fd021f	Quạt đứng Xiaomi	FAN	home/quat_ung_xiaomi	{}	2026-05-11 21:54:16.452958+07
e72633f1-87d7-43a8-bc1e-aaaab303c575	smart_light_philips	4bc80010-bebc-4f99-a448-3c1dfae5b8c6	Smart Light Philips	LIGHT	home/smart_light_philips	{}	2026-05-11 21:54:16.453499+07
c966ee3a-02cb-4732-96da-2554b55f8535	smart_ac_daikin	4bc80010-bebc-4f99-a448-3c1dfae5b8c6	Smart AC Daikin	AC	home/smart_ac_daikin	{}	2026-05-11 21:54:16.454063+07
91dbf2f8-0008-44fe-9737-96e527ffa930	smart_tv_backlight	4211dcf2-3b21-4094-9bd4-d3c3ef349f8a	Smart TV Backlight	LIGHT	home/smart_tv_backlight	{}	2026-05-11 21:54:16.454607+07
1ec52558-ddf2-465d-adf9-ce35a9c55fc4	garage_door_lock	d674aec4-2c57-498a-965b-55ce44e9b5d3	Garage Door Lock	LOCK	home/garage_door_lock	{}	2026-05-11 21:54:16.455215+07
ae384afc-80fa-4596-a9f5-54c514d7164e	garage_camera	d674aec4-2c57-498a-965b-55ce44e9b5d3	Garage Camera	CAMERA	home/garage_camera	{}	2026-05-11 21:54:16.455788+07
e3896e00-1c28-4d8b-98ae-17f4bb501e4f	quat_thong_gio	b9a3082e-2497-49f7-bd43-e7a729705f18	Quạt thông gió	FAN	home/quat_thong_gio	{}	2026-05-11 21:54:16.451802+07
097527ff-2aed-4d01-94ce-1642f36abee2	khoa_cua_smart_lock	b9a3082e-2497-49f7-bd43-e7a729705f18	Khóa cửa Smart Lock	LOCK	home/khoa_cua_smart_lock	{}	2026-05-11 21:54:16.445784+07
065dcd9c-7b1e-40f8-a1f0-ff1301dd9d3a	cam_bien_chuyen_ong_pir	81922cb9-60a4-4c70-abb8-55ff18e95097	Cảm biến chuyển động PIR	SENSOR	home/cam_bien_chuyen_ong_pir	{}	2026-05-11 21:54:16.448644+07
\.


--
-- TOC entry 5117 (class 0 OID 19060)
-- Dependencies: 242
-- Data for Name: energy_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.energy_logs (id, device_id, power_usage, "timestamp") FROM stdin;
79c927cf-1ee1-46f9-b252-185b9e7b6554	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.873	2026-05-13 13:54:16.464819
a9eb2fbe-33f0-4356-9980-267e713d801c	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.572	2026-05-13 07:54:16.464873
112e8f8f-44fe-459e-8a81-137508fb4021	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.29	2026-05-13 01:54:16.464898
a87e98d8-0f74-403a-bda4-d482ca260a11	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.243	2026-05-12 19:54:16.464915
cd0dc650-5437-4076-9529-ce3ad782f9dd	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.921	2026-05-12 13:54:16.46493
81fd0b9c-d22a-485c-b960-e1d563679ea0	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.892	2026-05-12 07:54:16.464944
94b7503c-e0c9-4a3b-9736-f83ba81c008c	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.852	2026-05-12 01:54:16.464957
cf771f2c-44a1-4b1e-98b5-77eeaf8f38f5	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.119	2026-05-11 19:54:16.46497
b9b7184b-6d46-4bda-a274-3a1a01554915	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.767	2026-05-11 13:54:16.464983
43018497-c25b-4d5c-ab1d-dcd3df41e514	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.575	2026-05-11 07:54:16.464994
35e429a1-a54d-473e-8d14-1f533a828b98	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.239	2026-05-11 01:54:16.465006
af89c511-82a7-46db-b61c-012ceec09973	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.5	2026-05-10 19:54:16.465018
f3c02cae-ae43-451a-9b85-76605e75a50d	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.573	2026-05-10 13:54:16.465031
0d787aa7-7794-4d9f-b68d-e85bd0899c55	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.657	2026-05-10 07:54:16.465042
00903e88-210b-4e79-ba8b-51b7b1f0b92d	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.631	2026-05-10 01:54:16.465054
d9f0a9c4-dc1c-4043-a531-21222f733aab	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.536	2026-05-09 19:54:16.465066
47126913-58c5-4b5a-be77-7c617dd8e56e	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.668	2026-05-09 13:54:16.465078
a0a6e228-1d91-4ddd-8829-13930388c898	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.849	2026-05-09 07:54:16.46509
447ca456-37f2-4753-8a9c-1c3c13533920	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.777	2026-05-09 01:54:16.465103
96b7136e-7c5f-4ae9-84e1-ab9631bbd4d9	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.046	2026-05-08 19:54:16.465115
171b6a77-132d-4ed2-9926-3bc60ce3b830	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.955	2026-05-08 13:54:16.465126
3172cae0-79f3-4728-aac5-c34dcc621b37	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.902	2026-05-08 07:54:16.465138
ca6c9434-bcc8-4bcd-aed7-1d99d10d5852	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.35	2026-05-08 01:54:16.465148
5841d606-b3fd-4e5e-bfa3-bee3618d3d0c	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.181	2026-05-07 19:54:16.46516
8ed5dcf6-e700-43e5-89ed-d9568a5ba4f5	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.029	2026-05-07 13:54:16.46517
82f3149f-8eaa-40ef-8e25-aadd42c92920	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.725	2026-05-07 07:54:16.465182
f1b9bf79-7b26-4e15-96e3-ee3abd168d07	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.124	2026-05-07 01:54:16.465195
bd1e4802-f0d9-43a1-ac63-e2f4105c8e76	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.128	2026-05-06 19:54:16.465207
29d3ebee-d9d8-409d-8d5a-c34590b1a923	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.975	2026-05-06 13:54:16.465218
18fee30f-0dfc-48ec-9747-467055354265	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.856	2026-05-06 07:54:16.46523
b117b4e6-40a8-4284-ad9e-33cada8da636	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.774	2026-05-06 01:54:16.465242
547853d9-aa06-4bf5-97b5-2ea53a529266	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.704	2026-05-05 19:54:16.465253
f16a00a4-b2c2-49a5-8519-09b9ec1c83d9	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.823	2026-05-05 13:54:16.465264
62078c8f-5a0c-42e7-ae4d-18032c62cf8f	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.037	2026-05-05 07:54:16.465277
2e512d59-d79f-442a-abc3-0c0ee0c79440	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.384	2026-05-05 01:54:16.465288
798957cd-673d-47fc-ac21-3f01958de45c	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.542	2026-05-04 19:54:16.465298
0e0cf1ce-2fb8-4650-be56-a89dedfc8681	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.966	2026-05-04 13:54:16.465309
45277bb2-11a4-453f-beee-96ebd2ba38bc	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.863	2026-05-04 07:54:16.46532
8b3e797b-504f-4dbf-bde5-8b6b806fd0ba	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.824	2026-05-04 01:54:16.465331
7e7aee7f-77e5-4f8a-b541-66cc3fa9bbdb	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.565	2026-05-03 19:54:16.465342
34c6d170-9a67-450c-8de4-e319bed29cd5	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.905	2026-05-03 13:54:16.465353
d012dbc1-fbb4-4d4b-b2a3-e0d83902ed34	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.582	2026-05-03 07:54:16.465365
ff503c28-7364-4361-9dc2-1af63fdaf688	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.247	2026-05-03 01:54:16.465424
4f66ae08-5e48-4716-9614-7e36d48904fd	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.303	2026-05-02 19:54:16.46546
8f285c9c-f9ca-473b-bfc6-b9ec9c50ffcc	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.599	2026-05-02 13:54:16.465479
d4f1d851-963b-465d-8a3f-731f000b22ca	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.674	2026-05-02 07:54:16.465495
97f9dc2e-0697-4140-a293-286d78da94e0	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.132	2026-05-02 01:54:16.46551
6c9c80cb-713d-4130-88dd-dab2d74b2677	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.293	2026-05-01 19:54:16.465523
2dd2dc5f-4551-450b-93de-58780ddd295b	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.871	2026-05-01 13:54:16.46554
160d9158-3c5d-4a98-b706-dda787cec64e	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.739	2026-05-01 07:54:16.46556
c6171920-591f-4d11-b1a0-3f021b473e46	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.377	2026-05-01 01:54:16.465576
29f061cc-de22-4d97-9c16-097ded1af426	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.231	2026-04-30 19:54:16.465589
c75a28bf-30ea-42ae-8e33-ba3851b40592	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.691	2026-04-30 13:54:16.465602
424d3a0a-f225-4b4f-944f-ef77f81285be	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.019	2026-04-30 07:54:16.465617
c816714c-cf9b-42c4-b59e-ee6fadef8ce0	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.63	2026-04-30 01:54:16.46563
88d712f4-6272-439c-9e5c-f9daf7f59605	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.594	2026-04-29 19:54:16.465642
7171c8af-2e24-4300-9989-3b1b4cab6043	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.644	2026-04-29 13:54:16.465653
39f27438-3bfd-4247-aa5a-2920c3c9cd3e	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.917	2026-04-29 07:54:16.465665
3001ee45-960c-4af1-871f-ffb3ac29d21e	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.189	2026-04-29 01:54:16.465677
d14ae399-51b3-4549-82d2-6d34007ffcc0	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.385	2026-04-28 19:54:16.465691
b20d5e2e-807b-467d-85d8-e0120ade5368	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.045	2026-04-28 13:54:16.465703
4e0dcff3-9ba1-4121-b9a2-b6e8a7ac15ec	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.874	2026-04-28 07:54:16.465714
e6dcd60c-ee18-4bce-8a5d-7f50535bb238	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.547	2026-04-28 01:54:16.465726
5da7f23b-e38e-472f-8b04-2e64407b94e0	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.663	2026-04-27 19:54:16.465738
4a2fb9a7-8380-4e62-9a6d-d2b825fe4712	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.973	2026-04-27 13:54:16.465749
7f0020eb-6bc9-466f-809e-4028dc263a17	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.94	2026-04-27 07:54:16.465761
a105ee95-6a4e-425e-9a61-d6d951c19842	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.248	2026-04-27 01:54:16.465772
16c5d3fd-f8a6-4d1c-87ca-6588eabb9452	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.069	2026-04-26 19:54:16.465783
f44c6998-b95e-428a-b91d-ad6444665222	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.715	2026-04-26 13:54:16.465795
3a50cc8d-70a9-4f3e-b98c-0dc000a7e5b0	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.691	2026-04-26 07:54:16.465806
0ebb50df-05e4-41ba-9d2b-448adc09b5c8	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.232	2026-04-26 01:54:16.46582
4e451393-9b66-4ec4-885b-e4821ab9037b	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.898	2026-04-25 19:54:16.465831
d7ac49e2-2074-4fa2-a508-dec243353a05	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.989	2026-04-25 13:54:16.465843
a95027d9-f4ef-40bb-bf64-e9403d47bfc2	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.714	2026-04-25 07:54:16.465854
5e9dad8c-f0ea-4d8d-97c2-83933f844ab3	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.636	2026-04-25 01:54:16.465866
ff322e93-d13d-4d6a-b3ad-4cbc8a194080	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.4	2026-04-24 19:54:16.465889
fb8a6bd4-2d97-44ab-9ccd-7ba39e49cf3d	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.008	2026-04-24 13:54:16.465903
6fccc24e-997f-4df9-8d1e-c29fc5bd3858	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.785	2026-04-24 07:54:16.465915
b983db63-1641-434c-a5b7-9ef43c18002f	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.281	2026-04-24 01:54:16.465927
0338e4b2-c591-453e-af62-ade9625b0c87	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.264	2026-04-23 19:54:16.465937
0fb778a6-abc4-4d1b-b309-92544acaba50	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.835	2026-04-23 13:54:16.465949
9a23e30b-a5aa-45e6-abaa-691fc249f717	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.689	2026-04-23 07:54:16.46596
dea6f4eb-003f-4c75-9fb8-8c7c24c53b22	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.572	2026-04-23 01:54:16.465972
19cffe6e-8805-4adb-ae73-99d2f4ae5601	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.857	2026-04-22 19:54:16.465982
e5bdc33f-a19f-4099-a988-9d6f52159099	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.756	2026-04-22 13:54:16.465994
f88310f5-b033-4d2a-9350-626825243ce2	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.667	2026-04-22 07:54:16.466005
e28f16c8-551e-4f30-bd06-f4f228d10ea7	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.948	2026-04-22 01:54:16.466017
bfdc16e7-97b7-46c2-be01-b665c810a3b0	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.504	2026-04-21 19:54:16.466028
99be466a-2c3d-4c3c-ad80-94d190288120	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.605	2026-04-21 13:54:16.466039
fe2ec6c7-6ea0-4ff4-a518-eef859da20f7	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.583	2026-04-21 07:54:16.46605
e232cca7-de1a-48e2-9670-fdb105e74f6d	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.14	2026-04-21 01:54:16.466061
ecc35d23-7a05-4188-9ff7-6ead350c929c	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.611	2026-04-20 19:54:16.466073
18d531f0-d3a0-4c75-921a-56e5b8d70cfa	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.948	2026-04-20 13:54:16.466084
980ff28d-edcf-436f-a176-9a461cc267fd	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.767	2026-04-20 07:54:16.466095
676de559-f61b-479a-b414-aa14ab249fb0	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.098	2026-04-20 01:54:16.466106
0362d12a-4197-411a-b2a9-ed0c7e054ac8	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.387	2026-04-19 19:54:16.466116
44a01a42-08db-49a3-a53c-5790976cef38	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.048	2026-04-19 13:54:16.466128
5cc9cb6f-7970-4249-826c-795741ba9d2f	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.819	2026-04-19 07:54:16.466139
b75cc0a1-982e-4d90-ac34-725acddda815	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.924	2026-04-19 01:54:16.466149
865c4a8e-158c-45cf-aaa8-593e156cb993	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.823	2026-04-18 19:54:16.46616
60468bff-8791-4c91-a42a-f75fae76e1b8	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.566	2026-04-18 13:54:16.46617
4f3aedf5-f2cf-4f88-84a6-eda4820f1862	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.913	2026-04-18 07:54:16.466181
18f86fa4-3db8-4d97-9d0e-dd4e49422e15	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.66	2026-04-18 01:54:16.466192
a1f86d18-2b6a-42ae-a990-529557127f30	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.529	2026-04-17 19:54:16.466204
b364c6df-ae34-4dc2-8752-880846f38811	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.691	2026-04-17 13:54:16.466215
3857ab96-dfea-428a-ba46-937d9a0b11b5	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.874	2026-04-17 07:54:16.466225
4db36025-21bf-45f5-a716-1305ee2bd4af	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.142	2026-04-17 01:54:16.466236
54ef9615-e8b8-40db-998e-48ab2a583f5e	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.436	2026-04-16 19:54:16.466247
65837997-d465-4a9d-bb2a-ef61ba4c9797	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.782	2026-04-16 13:54:16.466259
ca71329a-3898-442e-a6c8-e9ea2362dd07	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.027	2026-04-16 07:54:16.466272
44221f2d-8c51-429b-9c68-0cf21e89d225	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.837	2026-04-16 01:54:16.466285
57b38c42-9944-464d-a7f5-138dfc52697c	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.28	2026-04-15 19:54:16.466297
3c408ae6-2bf1-4f43-a3e7-f627a553d7c8	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.805	2026-04-15 13:54:16.466309
0ca48a4c-90f4-442d-9082-0060ac46a610	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.648	2026-04-15 07:54:16.466321
0049a64c-8084-4c0c-83cc-5ee3b6bbbecb	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.87	2026-04-15 01:54:16.466333
0f09cc72-ceed-4481-bdd1-f2b41f097014	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.832	2026-04-14 19:54:16.466345
7a011828-97ee-44cf-b8f3-ffdbd1dce3cc	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.706	2026-04-14 13:54:16.466356
a928574f-178e-4b54-9465-839bc4b29523	5617507e-4f26-467c-a39a-bbcf4ae37ca0	0.873	2026-04-14 07:54:16.466368
e8ed7291-5b02-415c-9e39-2d8c7ba17895	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.594	2026-04-14 01:54:16.466379
84261786-0b2b-4884-8892-dfaf2ba524d2	5617507e-4f26-467c-a39a-bbcf4ae37ca0	1.179	2026-04-13 19:54:16.466389
d66e0ae6-4edf-49e3-bc8f-c64d79b7f66a	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.74	2026-05-13 13:54:16.466402
826b8482-534d-4f9d-bcdb-8424c054619f	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.647	2026-05-13 07:54:16.466416
09c7c1f9-9dda-4217-b1a3-bfa76f8d4e3a	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.387	2026-05-13 01:54:16.466428
1206aa5f-0f88-4d66-9cae-021e4a07184d	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.194	2026-05-12 19:54:16.466439
5949d4f2-3a61-4e18-9076-6f47e96c9661	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.42	2026-05-12 13:54:16.466451
0c3ee119-8f53-4d39-a73d-a322ff98805d	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.556	2026-05-12 07:54:16.466462
9e66b394-2b61-4a3f-befb-eedfa40dfbad	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.795	2026-05-12 01:54:16.466474
ece514f0-01d3-4213-86a3-696898c12759	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.505	2026-05-11 19:54:16.466485
9bb42901-cd6b-4885-adea-7ce0de4d46a4	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.789	2026-05-11 13:54:16.466496
d3fa4929-0f3c-4636-8720-aaf3ddece3eb	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.769	2026-05-11 07:54:16.466507
59dbf073-e043-4f2b-a62f-984d555d66c9	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.02	2026-05-11 01:54:16.466518
a49ae29a-f77f-4e78-a141-1b3036950ace	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.825	2026-05-10 19:54:16.466529
12ceda96-fa5a-4c86-ad99-2dc58c6a966e	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.789	2026-05-10 13:54:16.466542
10b63331-6760-40c0-8c58-02137492660f	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.818	2026-05-10 07:54:16.466552
38460992-0380-4869-92cd-b5b9aca41fe7	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.847	2026-05-10 01:54:16.466563
23576657-1421-4d2b-8d7a-00573ca033bd	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.159	2026-05-09 19:54:16.466574
87531b19-7b59-4b85-a57b-953d60a08752	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.449	2026-05-09 13:54:16.466585
163d07e9-9601-4a44-a24f-35f2b99f5815	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.739	2026-05-09 07:54:16.466596
37810b27-b63a-4c39-a906-9cca229b49bd	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.377	2026-05-09 01:54:16.466607
fa0d66fb-00ce-4aaa-9c60-98c9ae1af8a0	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.88	2026-05-08 19:54:16.466618
e589cc38-d8ae-4729-9507-bb93f9457c90	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.62	2026-05-08 13:54:16.46663
26603dd4-4866-42c3-9b9d-3fc8f9ce6d64	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.651	2026-05-08 07:54:16.466641
aed53d5d-671f-4875-b5d8-af5c3c21a6b5	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.987	2026-05-08 01:54:16.466652
f3c337b0-b08d-4352-a20e-e9bc47e5c2b8	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.46	2026-05-07 19:54:16.466662
b24b1e92-5b99-4ce6-ac2f-87c159797a7a	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.598	2026-05-07 13:54:16.466673
3417fe62-9370-40cd-a823-99d96d76cce3	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.509	2026-05-07 07:54:16.466685
391978e7-a9dd-42da-9cbd-ceadf921d724	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.201	2026-05-07 01:54:16.466697
f26e07ba-7306-4552-97aa-b3aacbc4855e	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.349	2026-05-06 19:54:16.46671
80e029c0-c94d-4865-979b-a9100003e004	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.504	2026-05-06 13:54:16.466723
c2854483-a870-4db4-82cf-e3ac4ef30e83	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.551	2026-05-06 07:54:16.466735
355ac76a-3cbf-4d4e-b8c8-9e44e52d19f0	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.556	2026-05-06 01:54:16.466746
3ac475f6-ab71-473f-b595-46715ad7c1d7	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.287	2026-05-05 19:54:16.466757
1724995e-805b-49b0-a884-06619f28fc66	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.604	2026-05-05 13:54:16.466768
45b61f7b-d062-4f0c-8589-00ceaab9970b	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.637	2026-05-05 07:54:16.46678
2e7ad29b-afc1-45e5-a7dc-d2a510b35216	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.874	2026-05-05 01:54:16.466791
613eca43-23c6-4a51-a689-68e1269c15b4	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.955	2026-05-04 19:54:16.466802
c7899eff-3a16-4bfe-a6e7-b8871ca9aa86	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.562	2026-05-04 13:54:16.466813
62edb558-87e5-41a6-8a74-13dbd19393ec	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.667	2026-05-04 07:54:16.466825
9e7efc9f-ec4a-43ff-b46c-ad4490f4eb5c	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.959	2026-05-04 01:54:16.466836
79e4a776-bc33-4298-943a-f5dd88fce0c1	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.952	2026-05-03 19:54:16.466847
b1bcacbd-f087-4482-a1c6-cc7105b06486	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.45	2026-05-03 13:54:16.466859
fad86bf8-c77e-49fa-bfaa-03858b3d4d9e	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.685	2026-05-03 07:54:16.46687
bdd79203-d8c3-44d7-a21f-fb141439c822	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.959	2026-05-03 01:54:16.466881
ef4a440f-3ba1-4a65-8c04-985569ce6256	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.486	2026-05-02 19:54:16.466892
b700c43f-1260-4a14-9572-431ab3193e50	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.781	2026-05-02 13:54:16.466903
bdebc701-0ff4-44e1-aead-abc6d10da387	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.45	2026-05-02 07:54:16.466915
3a09dc28-d9fd-4d47-a1b4-51aed8bf67c5	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.966	2026-05-02 01:54:16.466928
5233ff34-4b24-4a4a-8618-3e94b5dc4e86	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.302	2026-05-01 19:54:16.466939
97383d17-6a0e-4bcf-87af-2dbf88b1c4bd	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.51	2026-05-01 13:54:16.46695
b20578d5-eb9e-48ca-a70c-f62401e7c211	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.476	2026-05-01 07:54:16.466962
e4358670-ae9e-4198-9e07-1ce15f7e81ff	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.51	2026-05-01 01:54:16.466972
4b3b28e3-d52f-4256-93a2-4ad39aef4d20	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.225	2026-04-30 19:54:16.466985
68878644-63c5-4523-ace5-ceec8ddfc9c3	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.619	2026-04-30 13:54:16.466996
0e4ac705-50f5-4e30-98f9-0a6bff635869	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.75	2026-04-30 07:54:16.467007
643d74cf-9d03-4d03-9894-46e3c7d654bd	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.41	2026-04-30 01:54:16.467018
7bf8c386-e67c-4443-8817-10c1f06c1380	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.929	2026-04-29 19:54:16.467029
f50aa528-0403-45a4-80ff-b848501ed34a	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.461	2026-04-29 13:54:16.46704
0f15e750-0de5-49a2-9d8e-fe8b9b6098f6	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.601	2026-04-29 07:54:16.467051
702c2f60-5b28-4220-b478-18c3f0cc6131	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.11	2026-04-29 01:54:16.467063
32b727ba-a8a4-4b21-b762-55614adedff5	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.144	2026-04-28 19:54:16.467073
8dd521d0-9e84-47ee-8bef-a2af734d43f9	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.726	2026-04-28 13:54:16.467085
4e2cd0cd-860d-4581-a1a8-3874cfb29da3	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.703	2026-04-28 07:54:16.467097
6036a898-d180-4382-a861-baa890ee05fd	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.548	2026-04-28 01:54:16.467108
99adad68-1c16-4bfc-9432-529a1ceea86b	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.857	2026-04-27 19:54:16.467119
0f04beeb-5334-498d-b4d1-a74febc05e6d	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.589	2026-04-27 13:54:16.46713
4bf6b7c5-82c3-4ed4-be00-984ad637e94a	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.563	2026-04-27 07:54:16.46714
6f37960a-5051-40be-8784-b746594749f4	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.452	2026-04-27 01:54:16.467153
2462d726-5c3f-455a-81ed-2df0e439b6ef	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.974	2026-04-26 19:54:16.467164
13844129-9796-4ff4-b6d3-ed5be76d9949	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.5	2026-04-26 13:54:16.467175
db3e984c-da37-4eaa-a089-94201c0c0765	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.608	2026-04-26 07:54:16.467187
1281c2ed-d165-4f7c-b007-7f18f9854d08	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.109	2026-04-26 01:54:16.467199
8d2779ac-5b00-464d-b4ff-26d462894502	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.997	2026-04-25 19:54:16.46721
028855da-01d5-47da-87be-44726a5c9ba9	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.525	2026-04-25 13:54:16.467221
e531fe2c-c4e5-41e9-beaf-89f14ccf2135	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.808	2026-04-25 07:54:16.467232
05c8a57c-5fd8-4fd4-b2b2-b66d565b87cf	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.126	2026-04-25 01:54:16.467243
31b8a124-c7c2-444a-839e-863461bc003b	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.452	2026-04-24 19:54:16.467254
5bf2e51b-dba3-4538-b124-707ba6548259	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.651	2026-04-24 13:54:16.467265
2291fc50-5026-4ce7-93e3-b279849f439f	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.441	2026-04-24 07:54:16.467276
7625e7be-0ed4-45e1-b147-348c3aa266dc	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.559	2026-04-24 01:54:16.467287
916693ae-4440-45df-9fcd-9a30c1fdc7f2	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.432	2026-04-23 19:54:16.467298
49315235-3329-4bc2-819a-4ff635473255	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.827	2026-04-23 13:54:16.467309
2021fc40-0204-406d-9e16-4a498f73b608	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.809	2026-04-23 07:54:16.46732
46590aec-9e83-4ef4-aceb-66922b6fb991	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.442	2026-04-23 01:54:16.467331
f7349bc1-9b3d-41a5-9a62-22cb03a9253c	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.91	2026-04-22 19:54:16.467342
c9584816-b376-46b0-933c-2a65cd87df0d	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.624	2026-04-22 13:54:16.467353
23fda610-a0ba-4f14-9a3b-5e4cd9526bc3	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.51	2026-04-22 07:54:16.467364
fe469a39-fd80-4f13-8b4d-1aa065693be1	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.093	2026-04-22 01:54:16.467375
6e87c931-094d-4c0a-acd0-8a4b16a5653e	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.826	2026-04-21 19:54:16.467386
429287ae-c9ef-4bb6-bbf5-fcfd98489159	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.579	2026-04-21 13:54:16.467397
d943536c-bc88-4494-b724-3d6acdf034d3	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.834	2026-04-21 07:54:16.467408
d88c4d66-a9b0-401f-9ff6-ea8f86861140	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.987	2026-04-21 01:54:16.467419
cf7bb540-e6fe-42ed-89f3-539ab7fda5ca	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.392	2026-04-20 19:54:16.46743
3699559f-52ac-4aa7-b3e6-f923636cce21	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.611	2026-04-20 13:54:16.467442
ac5e5a07-e70a-4fff-89ed-9e6982621db8	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.598	2026-04-20 07:54:16.467454
072cb95c-7c33-403b-af8b-81c758ed6d16	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.527	2026-04-20 01:54:16.467467
827aaaa3-1353-4dcf-86c1-09466d83d4ec	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.556	2026-04-19 19:54:16.467478
2ddc4d9e-2508-4d88-976a-5f05e6636ef6	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.653	2026-04-19 13:54:16.467489
0ff2d7cc-6c1b-469c-bc07-a6a2cfa19a27	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.722	2026-04-19 07:54:16.4675
2a56a749-b5df-47a4-899d-3812ca1d73f9	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.901	2026-04-19 01:54:16.467512
e2299e49-e5f3-45b7-bc7b-75eb62bf4cf0	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.011	2026-04-18 19:54:16.467524
e411e1c4-2b91-4e5d-86ee-a4aa370d5837	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.827	2026-04-18 13:54:16.467535
2af9da27-8c5c-4d05-a5d8-5445682fe2f6	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.663	2026-04-18 07:54:16.467546
23313e28-339f-4b6c-b522-d5745d0bd6e4	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.203	2026-04-18 01:54:16.467558
3b3fd8e7-4f9a-415a-bcc0-2838534d032b	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.363	2026-04-17 19:54:16.467569
e9a56f28-d29b-4beb-a96a-443d9feb1665	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.444	2026-04-17 13:54:16.46758
f80ed9e6-6308-4444-8cf7-547a5f3d73ae	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.665	2026-04-17 07:54:16.467591
2128ad95-9fe4-42fc-9c70-93dc521323f1	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.172	2026-04-17 01:54:16.467602
be54fefa-409c-4a8b-b6db-3e319ac0f1ad	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.445	2026-04-16 19:54:16.467613
1d7850f9-5275-4287-a57d-f15d81a9d1f7	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.486	2026-04-16 13:54:16.467624
2a4da314-7959-4557-8b22-21ecceb42861	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.824	2026-04-16 07:54:16.467636
48113309-80a3-4b27-a818-688d2a6baba6	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.842	2026-04-16 01:54:16.46772
4a95f5bb-54ed-4a61-b10e-7ba868705a22	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.925	2026-04-15 19:54:16.467735
e3956529-9b20-45fe-9766-9d2fbf574062	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.67	2026-04-15 13:54:16.467747
dcb1457c-55e4-4d8e-9775-3a863e259d3f	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.704	2026-04-15 07:54:16.467758
68d67369-83b9-4ab6-8fd1-9096aa1048dc	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.963	2026-04-15 01:54:16.467769
729e981d-0bf6-4d81-a619-e0c60d984357	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.874	2026-04-14 19:54:16.467781
e025ef94-eb50-446a-921b-fb192d2df685	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.794	2026-04-14 13:54:16.467792
ac0c7f84-a8e2-45b7-96d6-52a2a332cf6c	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	0.523	2026-04-14 07:54:16.467803
5e2fc4f8-b4bb-48de-a814-efe0751647d0	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.244	2026-04-14 01:54:16.467814
009f8636-83e3-4da3-a481-4e85f3a1351b	44d9d8a2-eb78-4b53-bef2-a3d84f127ba6	1.263	2026-04-13 19:54:16.467826
6916898e-873b-42c0-9f71-5c1be5f60ab8	8000d19f-46ee-4271-80b4-1168d1b1834e	0.019	2026-05-13 13:54:16.467838
dead41d5-ac10-418e-99dc-78503d6e8a81	8000d19f-46ee-4271-80b4-1168d1b1834e	0.023	2026-05-13 07:54:16.467851
3b7b2e7f-9bef-4c1f-beea-bd4c1db390db	8000d19f-46ee-4271-80b4-1168d1b1834e	0.04	2026-05-13 01:54:16.467864
af4697ad-9586-4166-b6d0-b36b1fdad6aa	8000d19f-46ee-4271-80b4-1168d1b1834e	0.062	2026-05-12 19:54:16.467876
a6b7b30b-53a1-4fcf-a357-9be1e85bb281	8000d19f-46ee-4271-80b4-1168d1b1834e	0.013	2026-05-12 13:54:16.467887
669ac663-0b52-49fd-98f4-9126d3bc391c	8000d19f-46ee-4271-80b4-1168d1b1834e	0.027	2026-05-12 07:54:16.467898
e85e6dc6-5500-4cfd-a2eb-99cb176efefd	8000d19f-46ee-4271-80b4-1168d1b1834e	0.025	2026-05-12 01:54:16.46791
a60dd7c0-9705-4fd8-b721-ed2cad2c3b70	8000d19f-46ee-4271-80b4-1168d1b1834e	0.034	2026-05-11 19:54:16.467921
8cfda452-7cd6-4464-832f-26fd919b79b2	8000d19f-46ee-4271-80b4-1168d1b1834e	0.026	2026-05-11 13:54:16.467932
a1f8a479-f25e-4969-ae2f-1f0691170848	8000d19f-46ee-4271-80b4-1168d1b1834e	0.015	2026-05-11 07:54:16.467944
557be398-0366-4ced-94ff-d80e7ff5ebdf	8000d19f-46ee-4271-80b4-1168d1b1834e	0.029	2026-05-11 01:54:16.467955
2063917a-e70a-44b0-9e4f-693d4a0e1685	8000d19f-46ee-4271-80b4-1168d1b1834e	0.052	2026-05-10 19:54:16.467967
81359bfd-afdb-422b-bf3c-721ba0cd8740	8000d19f-46ee-4271-80b4-1168d1b1834e	0.009	2026-05-10 13:54:16.467978
40f21e3d-0637-408a-a4f0-f05455d255db	8000d19f-46ee-4271-80b4-1168d1b1834e	0.02	2026-05-10 07:54:16.46799
8e156b2c-6a1f-44c1-a76c-febdb0a9dc7d	8000d19f-46ee-4271-80b4-1168d1b1834e	0.065	2026-05-10 01:54:16.468002
90a2b468-135d-4ed0-9860-fd9ad3f966cc	8000d19f-46ee-4271-80b4-1168d1b1834e	0.065	2026-05-09 19:54:16.468013
4b447e9b-991c-40c6-b038-d41185963947	8000d19f-46ee-4271-80b4-1168d1b1834e	0.009	2026-05-09 13:54:16.468023
b52d1037-8193-4e25-a821-a72060426378	8000d19f-46ee-4271-80b4-1168d1b1834e	0.013	2026-05-09 07:54:16.468035
8673f5aa-ce6e-4334-8283-b6a536c8fed5	8000d19f-46ee-4271-80b4-1168d1b1834e	0.027	2026-05-09 01:54:16.468046
f6a93336-02f6-4962-bbf0-82a5f20d800c	8000d19f-46ee-4271-80b4-1168d1b1834e	0.062	2026-05-08 19:54:16.468057
e63e42bb-4d4e-4559-8ec6-8cb88d3ff7db	8000d19f-46ee-4271-80b4-1168d1b1834e	0.032	2026-05-08 13:54:16.468068
62bd5ce5-5222-4572-944c-6a6ffce7cd6d	8000d19f-46ee-4271-80b4-1168d1b1834e	0.032	2026-05-08 07:54:16.468079
bc5e0421-096a-4338-b635-7de8ef0646ff	8000d19f-46ee-4271-80b4-1168d1b1834e	0.032	2026-05-08 01:54:16.46809
4e025ce2-c240-4aaa-8f93-7ba1e88be298	8000d19f-46ee-4271-80b4-1168d1b1834e	0.021	2026-05-07 19:54:16.468101
11767cbd-f3d0-43a2-9b1f-08a637ceb1ee	8000d19f-46ee-4271-80b4-1168d1b1834e	0.03	2026-05-07 13:54:16.468111
6607fc24-1666-49e3-bca3-577578366414	8000d19f-46ee-4271-80b4-1168d1b1834e	0.027	2026-05-07 07:54:16.468122
2161fb67-aee4-41f0-bf68-65b2fa1f5ebb	8000d19f-46ee-4271-80b4-1168d1b1834e	0.045	2026-05-07 01:54:16.468133
9ddc9bea-7e3e-4fae-9016-15e1caa3bb20	8000d19f-46ee-4271-80b4-1168d1b1834e	0.064	2026-05-06 19:54:16.468144
3f1b2bd3-8339-4e9d-8830-3fc91520d117	8000d19f-46ee-4271-80b4-1168d1b1834e	0.025	2026-05-06 13:54:16.468155
852cb3a8-85a2-4543-86e4-709575515b27	8000d19f-46ee-4271-80b4-1168d1b1834e	0.007	2026-05-06 07:54:16.468166
60a43850-764a-4f4b-bc17-4d8a9cbe8c1d	8000d19f-46ee-4271-80b4-1168d1b1834e	0.055	2026-05-06 01:54:16.468177
24e60b95-c978-4163-8dd3-7c5a503bf818	8000d19f-46ee-4271-80b4-1168d1b1834e	0.029	2026-05-05 19:54:16.46819
c18484bc-ec89-48ed-ab07-afa71344c62c	8000d19f-46ee-4271-80b4-1168d1b1834e	0.026	2026-05-05 13:54:16.468201
009bda0b-cf8e-4dea-b5fc-eaa84737a275	8000d19f-46ee-4271-80b4-1168d1b1834e	0.033	2026-05-05 07:54:16.468211
e60e97ad-3ed4-44fc-864a-2288d6ca7284	8000d19f-46ee-4271-80b4-1168d1b1834e	0.02	2026-05-05 01:54:16.468222
169ae74c-9ded-42b5-ab54-95de1cb15f2a	8000d19f-46ee-4271-80b4-1168d1b1834e	0.019	2026-05-04 19:54:16.468234
3ac53fb7-76e8-4a8d-b1ba-ec0cb49e5ef3	8000d19f-46ee-4271-80b4-1168d1b1834e	0.01	2026-05-04 13:54:16.468245
bac62cbc-3543-42a7-bffa-b23ddf01fc3b	8000d19f-46ee-4271-80b4-1168d1b1834e	0.022	2026-05-04 07:54:16.468255
f3aedb9f-4136-4541-9d80-8845e3d12e3e	8000d19f-46ee-4271-80b4-1168d1b1834e	0.027	2026-05-04 01:54:16.468266
6b30ff8e-46a7-4831-ad3e-672ac7b3aacd	8000d19f-46ee-4271-80b4-1168d1b1834e	0.044	2026-05-03 19:54:16.468277
a4f75659-55e2-4a07-b7cd-1f811aa6d250	8000d19f-46ee-4271-80b4-1168d1b1834e	0.027	2026-05-03 13:54:16.468288
ba24c8b4-3c60-421b-a5a8-287f14016b48	8000d19f-46ee-4271-80b4-1168d1b1834e	0.013	2026-05-03 07:54:16.468298
fbe22ab6-d35a-4254-88dd-8e3f59756b9a	8000d19f-46ee-4271-80b4-1168d1b1834e	0.046	2026-05-03 01:54:16.468309
7dc11915-8a45-43a1-ae0d-5335326ef1ba	8000d19f-46ee-4271-80b4-1168d1b1834e	0.027	2026-05-02 19:54:16.468321
47a31b4c-388f-4ad1-895d-fc186d2a46bd	8000d19f-46ee-4271-80b4-1168d1b1834e	0.021	2026-05-02 13:54:16.468332
ea115689-118a-4996-bcb7-66b804432630	8000d19f-46ee-4271-80b4-1168d1b1834e	0.032	2026-05-02 07:54:16.468343
eeb0d79e-7bef-47d4-9d78-84d39d395116	8000d19f-46ee-4271-80b4-1168d1b1834e	0.057	2026-05-02 01:54:16.468355
6bd139a2-1443-4585-888c-720188ac1998	8000d19f-46ee-4271-80b4-1168d1b1834e	0.018	2026-05-01 19:54:16.468367
1f7d0d7e-84b2-4151-abf0-a0c7b8abaea4	8000d19f-46ee-4271-80b4-1168d1b1834e	0.019	2026-05-01 13:54:16.468378
ecb23cd8-7653-431d-978b-adebc8002bab	8000d19f-46ee-4271-80b4-1168d1b1834e	0.015	2026-05-01 07:54:16.468389
6d79a474-c6d8-488c-8141-ac076cf5026e	8000d19f-46ee-4271-80b4-1168d1b1834e	0.013	2026-05-01 01:54:16.4684
77ab3d93-6a4a-44bd-a8ed-9ef1b94b66cf	8000d19f-46ee-4271-80b4-1168d1b1834e	0.053	2026-04-30 19:54:16.468411
3708c5aa-7802-4a34-af32-f348025a4598	8000d19f-46ee-4271-80b4-1168d1b1834e	0.025	2026-04-30 13:54:16.468422
cbed344b-dd3b-4366-be3b-d9b9bbfef49c	8000d19f-46ee-4271-80b4-1168d1b1834e	0.014	2026-04-30 07:54:16.468434
d2a54c01-5a2e-4ffc-9fa5-07297d7044b1	8000d19f-46ee-4271-80b4-1168d1b1834e	0.052	2026-04-30 01:54:16.468445
d3352599-81b8-4f0b-8f28-d561d1ac42e5	8000d19f-46ee-4271-80b4-1168d1b1834e	0.042	2026-04-29 19:54:16.468456
bd5115ec-1bc1-4ec3-bfbb-3bdb8d21cd8d	8000d19f-46ee-4271-80b4-1168d1b1834e	0.019	2026-04-29 13:54:16.468467
658b55e1-925e-4de9-94c8-7a1bd71228ae	8000d19f-46ee-4271-80b4-1168d1b1834e	0.007	2026-04-29 07:54:16.468478
e713ad7c-a22a-443c-a620-9d82c4f3b9df	8000d19f-46ee-4271-80b4-1168d1b1834e	0.017	2026-04-29 01:54:16.468489
0795bab8-b8dd-4450-8d8d-ac57cb426e37	8000d19f-46ee-4271-80b4-1168d1b1834e	0.059	2026-04-28 19:54:16.468501
24653ad9-8bd0-47bd-8579-aa33f9b03528	8000d19f-46ee-4271-80b4-1168d1b1834e	0.032	2026-04-28 13:54:16.468512
d0dd900f-a901-40db-ab7d-fb47f9229645	8000d19f-46ee-4271-80b4-1168d1b1834e	0.022	2026-04-28 07:54:16.468523
99dcdb19-7f2e-4547-b864-4f71ba087883	8000d19f-46ee-4271-80b4-1168d1b1834e	0.056	2026-04-28 01:54:16.468534
177ee50d-2ad6-44af-8b55-97abf7155937	8000d19f-46ee-4271-80b4-1168d1b1834e	0.043	2026-04-27 19:54:16.468548
800db02d-05ed-482b-9f7f-71a9e94b1c10	8000d19f-46ee-4271-80b4-1168d1b1834e	0.011	2026-04-27 13:54:16.468559
54460665-1325-4a35-8b75-a1e9fe448a86	8000d19f-46ee-4271-80b4-1168d1b1834e	0.011	2026-04-27 07:54:16.46857
c9b1478a-88fc-4954-8b10-d3142afb9f6f	8000d19f-46ee-4271-80b4-1168d1b1834e	0.029	2026-04-27 01:54:16.468581
c0a45fd5-10ae-4aff-95e0-857fa9fed168	8000d19f-46ee-4271-80b4-1168d1b1834e	0.06	2026-04-26 19:54:16.468592
71d42fab-4235-482f-95cc-1dd8e2bcee06	8000d19f-46ee-4271-80b4-1168d1b1834e	0.029	2026-04-26 13:54:16.468603
b119e6a0-f919-4623-91a8-ff14ec548d7f	8000d19f-46ee-4271-80b4-1168d1b1834e	0.031	2026-04-26 07:54:16.468614
3d038858-3298-417e-851c-dd597dc9dc47	8000d19f-46ee-4271-80b4-1168d1b1834e	0.06	2026-04-26 01:54:16.468625
5abec37f-b382-449f-8963-fe65f08b8a0e	8000d19f-46ee-4271-80b4-1168d1b1834e	0.024	2026-04-25 19:54:16.468636
b63f125c-e1e2-4a02-8ec5-158f7ec33882	8000d19f-46ee-4271-80b4-1168d1b1834e	0.014	2026-04-25 13:54:16.468647
92e5f046-a86b-4a95-95eb-56f0d230a491	8000d19f-46ee-4271-80b4-1168d1b1834e	0.01	2026-04-25 07:54:16.468659
96dc1626-fab1-411d-9a43-62b63c40428a	8000d19f-46ee-4271-80b4-1168d1b1834e	0.054	2026-04-25 01:54:16.46867
b0dcd756-e9e7-4289-bec7-9d9ab8729b81	8000d19f-46ee-4271-80b4-1168d1b1834e	0.059	2026-04-24 19:54:16.468681
e234937d-000e-4b2f-b254-ec17e544b51f	8000d19f-46ee-4271-80b4-1168d1b1834e	0.018	2026-04-24 13:54:16.468691
80242017-03f1-4304-95a9-af2a3beb4207	8000d19f-46ee-4271-80b4-1168d1b1834e	0.024	2026-04-24 07:54:16.468702
b165c3ea-977a-4cb8-9b23-08e0ba74b063	8000d19f-46ee-4271-80b4-1168d1b1834e	0.021	2026-04-24 01:54:16.468713
fc4a04de-3f93-4850-891b-2d47d234cd01	8000d19f-46ee-4271-80b4-1168d1b1834e	0.061	2026-04-23 19:54:16.468723
8e3d0919-a762-4855-962f-c5833891ec3b	8000d19f-46ee-4271-80b4-1168d1b1834e	0.031	2026-04-23 13:54:16.468734
d50946f8-2b9c-4d20-a638-c13b3e3f513e	8000d19f-46ee-4271-80b4-1168d1b1834e	0.034	2026-04-23 07:54:16.468746
d4ac8c21-9473-4dbe-a4ce-ba83b22a0116	8000d19f-46ee-4271-80b4-1168d1b1834e	0.055	2026-04-23 01:54:16.468758
441a272d-9f88-4fb8-a51e-870da3fa4340	8000d19f-46ee-4271-80b4-1168d1b1834e	0.059	2026-04-22 19:54:16.46877
1070f3ad-10b7-4b63-844d-531285e28020	8000d19f-46ee-4271-80b4-1168d1b1834e	0.008	2026-04-22 13:54:16.468781
63b119c1-52a3-46c6-afbc-25e3f8c56739	8000d19f-46ee-4271-80b4-1168d1b1834e	0.028	2026-04-22 07:54:16.468793
9d913813-929a-400e-b0b9-93d6686d6be1	8000d19f-46ee-4271-80b4-1168d1b1834e	0.03	2026-04-22 01:54:16.468804
3b48d44a-160a-463c-b9f1-8a865acec875	8000d19f-46ee-4271-80b4-1168d1b1834e	0.061	2026-04-21 19:54:16.468815
bb6887ce-866e-4c23-b24f-3415f8735f85	8000d19f-46ee-4271-80b4-1168d1b1834e	0.029	2026-04-21 13:54:16.468827
45f2ac9d-3e89-43a8-b6f0-45ab3b59adcc	8000d19f-46ee-4271-80b4-1168d1b1834e	0.031	2026-04-21 07:54:16.468838
67120aef-2a86-4dd9-9736-55b93a2d6569	8000d19f-46ee-4271-80b4-1168d1b1834e	0.055	2026-04-21 01:54:16.468848
055fe29d-76b5-4d11-b71c-b89828253b4c	8000d19f-46ee-4271-80b4-1168d1b1834e	0.027	2026-04-20 19:54:16.468859
ba2136c3-ac25-4b71-a955-92b87cc8cf61	8000d19f-46ee-4271-80b4-1168d1b1834e	0.029	2026-04-20 13:54:16.468871
e503ab1d-92aa-44a9-b4a2-f2f86a229207	8000d19f-46ee-4271-80b4-1168d1b1834e	0.01	2026-04-20 07:54:16.468882
7e326a90-0d60-46b6-b6c5-abb9f1676272	8000d19f-46ee-4271-80b4-1168d1b1834e	0.058	2026-04-20 01:54:16.468893
7850ec8e-9b50-4a5f-a2f2-79589b9a079f	8000d19f-46ee-4271-80b4-1168d1b1834e	0.058	2026-04-19 19:54:16.468905
48ca4e0d-a039-4eb9-988f-a8641343288f	8000d19f-46ee-4271-80b4-1168d1b1834e	0.013	2026-04-19 13:54:16.468915
984322b0-291c-4d26-a536-38665f3cbc4c	8000d19f-46ee-4271-80b4-1168d1b1834e	0.03	2026-04-19 07:54:16.468926
416fba40-f20a-4a79-8fda-1fdf10336008	8000d19f-46ee-4271-80b4-1168d1b1834e	0.037	2026-04-19 01:54:16.468937
a4a2980f-ebf4-4cdb-bcc7-f49e0627590d	8000d19f-46ee-4271-80b4-1168d1b1834e	0.029	2026-04-18 19:54:16.468947
914d1b05-9290-4343-bec8-13fe88fd5a8d	8000d19f-46ee-4271-80b4-1168d1b1834e	0.029	2026-04-18 13:54:16.468959
ef316c32-a8b0-4187-a566-b170cc63922f	8000d19f-46ee-4271-80b4-1168d1b1834e	0.013	2026-04-18 07:54:16.46897
9f49a6f3-7a20-40dd-b6ed-22955386a579	8000d19f-46ee-4271-80b4-1168d1b1834e	0.014	2026-04-18 01:54:16.468984
e768dd15-87f3-405a-b44d-8071197f7549	8000d19f-46ee-4271-80b4-1168d1b1834e	0.023	2026-04-17 19:54:16.468994
eaef192b-08dd-42a1-a34f-55a473384d87	8000d19f-46ee-4271-80b4-1168d1b1834e	0.016	2026-04-17 13:54:16.469005
e81e0b92-1b0f-46b9-876a-f081bac12b9b	8000d19f-46ee-4271-80b4-1168d1b1834e	0.031	2026-04-17 07:54:16.469016
68ecc856-260b-4032-aa84-391092484a9e	8000d19f-46ee-4271-80b4-1168d1b1834e	0.063	2026-04-17 01:54:16.469026
c637a8d8-764f-4512-8b9f-1256405c8a9a	8000d19f-46ee-4271-80b4-1168d1b1834e	0.028	2026-04-16 19:54:16.469037
099f348d-44ab-478c-97ac-afd9b591c60a	8000d19f-46ee-4271-80b4-1168d1b1834e	0.025	2026-04-16 13:54:16.469048
c47c6c7b-dcdc-43fb-bad2-47d40f394fcc	8000d19f-46ee-4271-80b4-1168d1b1834e	0.018	2026-04-16 07:54:16.46906
30b61b17-06ed-4997-91f9-b026358fa290	8000d19f-46ee-4271-80b4-1168d1b1834e	0.064	2026-04-16 01:54:16.469071
f8f97595-e2b6-49de-9df3-8299a81a66cd	8000d19f-46ee-4271-80b4-1168d1b1834e	0.041	2026-04-15 19:54:16.469082
eb89ff0c-e8f1-4586-8f43-3e4a12b34ffc	8000d19f-46ee-4271-80b4-1168d1b1834e	0.033	2026-04-15 13:54:16.469093
7df90ccb-03be-4121-a656-856a1dcc3f71	8000d19f-46ee-4271-80b4-1168d1b1834e	0.01	2026-04-15 07:54:16.469103
01445972-2332-4e1a-99c9-1a0bcb7c6ae4	8000d19f-46ee-4271-80b4-1168d1b1834e	0.063	2026-04-15 01:54:16.469115
978e10cc-2490-4d0a-9700-9832c146ac7d	8000d19f-46ee-4271-80b4-1168d1b1834e	0.022	2026-04-14 19:54:16.469126
7affa8b8-6162-41f6-9030-8f9e0cf431cc	8000d19f-46ee-4271-80b4-1168d1b1834e	0.034	2026-04-14 13:54:16.469137
0cf2f697-cdc3-4a0d-b350-3919799e44fb	8000d19f-46ee-4271-80b4-1168d1b1834e	0.014	2026-04-14 07:54:16.469148
97dfa83c-90f0-4041-810e-93fa6f83f1f5	8000d19f-46ee-4271-80b4-1168d1b1834e	0.019	2026-04-14 01:54:16.469158
c17bea3f-d5f5-466d-9eea-5cf9551e2c37	8000d19f-46ee-4271-80b4-1168d1b1834e	0.036	2026-04-13 19:54:16.46917
d9dc14a8-8ea9-4617-b559-d14f821b1544	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.034	2026-05-13 13:54:16.469181
d98fa918-9b13-4f6b-9a7c-fb6e9f4ab815	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.023	2026-05-13 07:54:16.469193
32dca604-c5f8-47a3-bc6d-fbfa3e79c756	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.058	2026-05-13 01:54:16.469205
2e2ef070-5633-4daf-8ad1-8d5c0beee3d1	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.053	2026-05-12 19:54:16.469216
ed844189-ae02-4e76-8fab-f74114f281d3	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.025	2026-05-12 13:54:16.469227
c093bb96-2f82-47d0-a3a9-8d6148412a05	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.03	2026-05-12 07:54:16.469239
71760ef2-aea5-4561-b5b9-e9f2b37d75ac	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.039	2026-05-12 01:54:16.469251
bee3550b-3000-42d2-89c8-d58839096053	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.063	2026-05-11 19:54:16.469262
1087d99b-623d-4008-9201-57480e2b0dbe	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.014	2026-05-11 13:54:16.469274
fd8a16c4-c286-4fde-a4e1-aeb264756a4e	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.04	2026-05-11 07:54:16.469284
b77a8c90-049d-4879-9ec9-3524ac3230d6	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.054	2026-05-11 01:54:16.469296
584a933d-66c8-43f3-889e-31ef6470eb8d	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.063	2026-05-10 19:54:16.469306
27357a00-9a80-4028-9183-9cc560127f8f	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.035	2026-05-10 13:54:16.469317
c57447e8-05d6-4ef5-89f2-dd7a1832b5ae	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.033	2026-05-10 07:54:16.469328
37c1db40-6283-4d48-aab1-c929293eaf6e	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.045	2026-05-10 01:54:16.469339
1240aa14-a829-4b05-a447-0438bc5cba58	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.03	2026-05-09 19:54:16.46935
a862b8a4-1dfb-4a34-9d43-027d10d9a68c	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.033	2026-05-09 13:54:16.469361
cd574934-4fde-45f3-bfa3-ee276fbfbfaf	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.023	2026-05-09 07:54:16.469372
1629d67e-7ad8-4178-a2f1-8d368388630a	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.042	2026-05-09 01:54:16.469385
2c890b6f-f3d2-43cc-b2bf-bf62e992b5e5	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.07	2026-05-08 19:54:16.469396
7610f056-5e24-43da-886b-e1887e579db4	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.034	2026-05-08 13:54:16.469406
7c2e5b4a-3ad2-49ff-b8bf-d9e288cf8dcd	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.022	2026-05-08 07:54:16.469418
550914a2-0316-47dc-a2b7-1ca79775fc03	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.042	2026-05-08 01:54:16.469429
069cb12b-1357-4f8a-a0bc-7c096be35eba	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.047	2026-05-07 19:54:16.469441
1507c9f9-37a2-4a5d-aa3a-340cbc6741ae	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.025	2026-05-07 13:54:16.469452
3744a1ab-a542-4f25-8990-13183579ca23	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.022	2026-05-07 07:54:16.469463
444d364a-3c41-4681-adba-56a7e3c864da	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.033	2026-05-07 01:54:16.469473
a6264be9-441c-4a2e-aafe-edb39781d5cd	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.048	2026-05-06 19:54:16.469484
f05ea0dd-94d7-4943-9e77-768fbe38b582	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.04	2026-05-06 13:54:16.469495
a7a69308-5ce9-45ee-a461-e342ddae2725	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.033	2026-05-06 07:54:16.469506
b753605f-fec2-434a-b7e3-80702f2ade51	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.073	2026-05-06 01:54:16.469516
7ad484ee-cb97-45bf-9a1e-c1a4bf65b930	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.058	2026-05-05 19:54:16.469527
270bfc8a-2f92-4a1a-8618-76e82377fa45	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.022	2026-05-05 13:54:16.469538
0fbd488a-346e-4526-86fa-3f5617517955	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.029	2026-05-05 07:54:16.469548
77677a9b-aba1-4eba-a399-1491dcf27cb7	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.026	2026-05-05 01:54:16.469558
5939f093-6a35-4fbb-acc3-00205937eb5d	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.041	2026-05-04 19:54:16.469569
d309b149-cf64-47d4-aed9-3a0b666c2862	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.026	2026-05-04 13:54:16.469581
5d10cede-0688-4d46-af04-3fe40c2529af	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.03	2026-05-04 07:54:16.469592
7e99257f-b398-40ba-89e6-b114bf53619c	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.06	2026-05-04 01:54:16.469603
d46d9622-6c11-4f3d-84f3-9099320c4f3a	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.05	2026-05-03 19:54:16.469614
e5bbf697-cc67-4f38-a62a-cb7b4c9e833e	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.026	2026-05-03 13:54:16.469626
34b832e3-ac27-40db-ae17-ed0e80e20839	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.02	2026-05-03 07:54:16.469636
e27a9986-f870-42a4-9f20-ead65468b814	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.051	2026-05-03 01:54:16.469648
3eef4c47-f362-4c84-86c1-bf076b6f617b	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.073	2026-05-02 19:54:16.469659
3ef61fe1-06b1-4602-b7d1-a5379a2ef442	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.036	2026-05-02 13:54:16.469672
7d16dd6a-cacb-48b5-af7e-e02716f2d202	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.019	2026-05-02 07:54:16.469683
3fe09b1c-2568-4bd7-89ec-7e284e84d49d	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.03	2026-05-02 01:54:16.469694
4de2961f-ee52-4f0f-973f-f63effbb5f59	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.053	2026-05-01 19:54:16.469705
a2a68861-25d8-47fe-b583-d7933136f2a1	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.032	2026-05-01 13:54:16.469716
94684e28-810c-4d80-894c-7043d549d6d6	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.023	2026-05-01 07:54:16.469727
7ed62274-e163-4ffe-a14b-8cf2cebee99a	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.069	2026-05-01 01:54:16.469738
49f30b2e-9ea8-4dc4-b4b3-24af2604e109	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.065	2026-04-30 19:54:16.469749
6ede615b-c1ad-440c-9e9d-03350fa71e03	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.033	2026-04-30 13:54:16.469759
34568496-5e8b-4c94-aa8d-13c8a2675361	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.02	2026-04-30 07:54:16.46977
27300d86-0a1e-43cf-85c3-5316050ce1fc	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.036	2026-04-30 01:54:16.46978
48852b9f-631f-421a-b3b0-ebd657fb5469	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.027	2026-04-29 19:54:16.469792
c00166bc-c75c-4c83-89bb-81309a2db79c	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.021	2026-04-29 13:54:16.469804
0ec8ad40-1660-4189-b473-0b8c6a68fae7	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.027	2026-04-29 07:54:16.469814
2db195a7-d8fb-455e-a92a-3d912dcd40c9	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.07	2026-04-29 01:54:16.469826
bfa75e6a-2e4c-4807-ba3e-6d559f61dc47	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.03	2026-04-28 19:54:16.469836
25735362-199b-4fa5-bfe7-282d86c107eb	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.026	2026-04-28 13:54:16.46985
02893c4a-8330-46d1-8cdd-d68f5c5a7c52	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.032	2026-04-28 07:54:16.469861
a7c68e13-95ef-4d53-921c-a877cc2da4f7	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.036	2026-04-28 01:54:16.469872
7d9df6be-8406-4647-b3fd-5021d0e2c505	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.062	2026-04-27 19:54:16.469882
6939b023-bbf4-4ee5-b43b-a8f201255a52	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.028	2026-04-27 13:54:16.469894
fb585902-767c-4cce-b28f-d6637811c071	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.021	2026-04-27 07:54:16.469904
a42c0f79-fadc-4d89-89e0-e077d4e56b04	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.06	2026-04-27 01:54:16.469916
4cc2f9b7-45d3-464d-9a53-8615afd8ec4b	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.026	2026-04-26 19:54:16.469927
6d074655-516e-4ad3-97ca-a37062ac2c72	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.035	2026-04-26 13:54:16.469938
937907df-e93a-4360-9831-586f96152f8a	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.036	2026-04-26 07:54:16.46995
3b483abf-51bf-49d8-a207-45b22465cae4	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.032	2026-04-26 01:54:16.469961
aa1dbadf-04b6-4b6e-8160-f2f6c27a62e8	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.048	2026-04-25 19:54:16.469972
165bbba2-19a6-4f72-8399-4b4b0d3145ae	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.019	2026-04-25 13:54:16.469984
0bd0f667-cad7-47eb-9252-7240cb324d9f	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.041	2026-04-25 07:54:16.469994
12efb54e-09f7-4f60-96be-ba5c134daede	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.053	2026-04-25 01:54:16.470005
fe880fc6-9c5a-4781-aa62-b56c661f15bc	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.029	2026-04-24 19:54:16.470016
c70392e7-ec77-4938-98f0-c91e50257f7a	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.021	2026-04-24 13:54:16.470027
956e5427-c59a-43ea-91ac-8c0e1ca07c61	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.038	2026-04-24 07:54:16.470038
ac534919-402f-4ee1-9491-70f8cd233c61	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.05	2026-04-24 01:54:16.470051
da1bbacf-17f3-4bba-909d-7123d2f9afff	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.068	2026-04-23 19:54:16.470061
2d3073e3-087c-4869-93f7-ffac15f52841	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.033	2026-04-23 13:54:16.470073
9eb4b8fa-51df-48de-b589-2a26e259d6a9	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.042	2026-04-23 07:54:16.470086
26a87126-3ac4-427c-ace6-694e0017fb64	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.057	2026-04-23 01:54:16.470098
d04d8cd3-3d53-41cc-a19d-2333cd8a1146	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.075	2026-04-22 19:54:16.470109
45252226-7ecf-49d0-90dd-40d77ac74fbd	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.039	2026-04-22 13:54:16.47012
3ef2ffd8-77ff-4371-8c71-d55cf57bc01a	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.031	2026-04-22 07:54:16.470131
efb4c9bc-a14f-4c00-9421-ec3ecbd3be51	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.063	2026-04-22 01:54:16.470142
d2a41451-f864-4141-a9a8-239bc131a399	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.052	2026-04-21 19:54:16.470153
50f8fe9b-857b-42ec-83ba-c7b7626ce91f	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.037	2026-04-21 13:54:16.470163
17953b33-f007-4d2f-b208-ced42aa4c9cd	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.029	2026-04-21 07:54:16.470174
770a52f9-65c8-44d0-9bb5-a42d4307e375	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.073	2026-04-21 01:54:16.470185
2a905f3b-3baf-4c90-8cad-ef45b633acc2	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.065	2026-04-20 19:54:16.470195
9905f87b-7208-4a7f-b0de-b32f80e4907d	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.027	2026-04-20 13:54:16.470255
eefd2a49-1ecb-4aa9-938e-a8a51dabd8b4	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.021	2026-04-20 07:54:16.470267
a4b33bf4-f9d8-42f9-bf45-dcd17299f449	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.039	2026-04-20 01:54:16.470278
63a5697c-5372-40c0-a7a2-5baa736b55e1	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.059	2026-04-19 19:54:16.47029
66cd21b7-7dc2-49ff-a42d-d042de144407	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.035	2026-04-19 13:54:16.470302
2c51e437-3ccc-4e9f-8cc0-a287575ef0cc	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.029	2026-04-19 07:54:16.470313
5a539ed1-8a27-4f36-a3fd-a4b5cb9eb2f2	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.059	2026-04-19 01:54:16.470323
061216ba-f024-43a4-9c5e-b8ad79c41423	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.04	2026-04-18 19:54:16.470334
01036cff-fb81-4c01-9064-6aa1c6083d3b	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.016	2026-04-18 13:54:16.470345
48e35dc8-1072-4987-9de3-89f796ffa5e3	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.022	2026-04-18 07:54:16.470355
dd335cd8-b29d-4fc4-9c7c-9ef48a7303b9	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.04	2026-04-18 01:54:16.470365
26ba2dfd-cf15-438c-bfa6-fb1b608db391	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.043	2026-04-17 19:54:16.470376
3f64b034-311f-4e0a-b757-2fc36d955c29	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.029	2026-04-17 13:54:16.470399
ebea6cd9-31e8-4f0c-a9ff-81871e274ac5	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.018	2026-04-17 07:54:16.470412
1e75d2fd-ba95-4b1a-bef6-968e34a20b2e	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.038	2026-04-17 01:54:16.470426
fa227481-7efd-4782-9d13-1599a7721847	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.062	2026-04-16 19:54:16.470438
01578742-60df-428c-b999-1c229ca68a10	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.034	2026-04-16 13:54:16.47045
90935ea0-5c3e-455c-a6ec-b9fb9fbab3d6	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.016	2026-04-16 07:54:16.470462
67c81220-b288-4422-939e-4962b0098c5e	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.047	2026-04-16 01:54:16.470474
7a3c7aff-8427-4fda-8cd3-a008abc9d961	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.054	2026-04-15 19:54:16.470484
68202382-49e7-4646-8ff7-f72ba03523df	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.026	2026-04-15 13:54:16.470495
e77d7984-4c1e-482a-a3c7-9f3a20ddcfaa	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.02	2026-04-15 07:54:16.470506
8a5637ca-f615-4a63-9109-909ba9bee8d7	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.048	2026-04-15 01:54:16.470518
1531f1f5-752c-4e06-b223-f322851cfe09	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.073	2026-04-14 19:54:16.470529
57b60c91-fba8-4695-a236-ab10f2100995	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.03	2026-04-14 13:54:16.470539
138d3034-58f1-428a-bf75-5e16877363be	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.033	2026-04-14 07:54:16.470551
3ebee782-cc9c-4bb6-a371-e32a4c9459bb	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.071	2026-04-14 01:54:16.470563
87a91505-5196-4abd-b5e9-f9a4ead8b56b	d107b36e-9576-4ab4-877e-8facd4dd2a29	0.066	2026-04-13 19:54:16.470573
0293bb58-8488-42db-821c-8248c08140e5	d578ad21-d98c-414a-b66a-df86446d4886	0.015	2026-05-13 13:54:16.470587
47997a8e-161c-4e6c-8a0a-938f3c28ba92	d578ad21-d98c-414a-b66a-df86446d4886	0.007	2026-05-13 07:54:16.470599
ffa7f211-e50d-48e7-8a88-3af0d878b40e	d578ad21-d98c-414a-b66a-df86446d4886	0.027	2026-05-13 01:54:16.470612
77c22b15-c721-4792-961d-e5324de9697f	d578ad21-d98c-414a-b66a-df86446d4886	0.042	2026-05-12 19:54:16.470624
b1037872-1876-4b35-826b-3a5fa46865a0	d578ad21-d98c-414a-b66a-df86446d4886	0.025	2026-05-12 13:54:16.470636
44f1031c-1537-4125-945c-488784a9a4e0	d578ad21-d98c-414a-b66a-df86446d4886	0.027	2026-05-12 07:54:16.470647
1ff9fcd7-a8b2-4681-9748-40a060cc6b62	d578ad21-d98c-414a-b66a-df86446d4886	0.029	2026-05-12 01:54:16.470658
6c846f1f-2cfe-45ce-bcf0-2a17a3f2264e	d578ad21-d98c-414a-b66a-df86446d4886	0.042	2026-05-11 19:54:16.470669
16f0e34c-76bf-4212-b3d8-1ca5850913a6	d578ad21-d98c-414a-b66a-df86446d4886	0.018	2026-05-11 13:54:16.470679
d97999bc-9610-445a-90db-10a400318f47	d578ad21-d98c-414a-b66a-df86446d4886	0.02	2026-05-11 07:54:16.470689
8114d16e-3417-405c-920f-f5c21614182c	d578ad21-d98c-414a-b66a-df86446d4886	0.022	2026-05-11 01:54:16.470701
49e30271-8294-4750-9d68-6c7720eb53d4	d578ad21-d98c-414a-b66a-df86446d4886	0.022	2026-05-10 19:54:16.470712
52d8152d-1fd5-413a-bd28-fce42d166722	d578ad21-d98c-414a-b66a-df86446d4886	0.016	2026-05-10 13:54:16.470723
45bfe3d5-cc67-4ad9-bf1c-b52aa6abe9af	d578ad21-d98c-414a-b66a-df86446d4886	0.008	2026-05-10 07:54:16.470735
9f640231-3ad5-4691-8b27-927eee29e6e4	d578ad21-d98c-414a-b66a-df86446d4886	0.026	2026-05-10 01:54:16.470747
14c51f4b-015e-4338-b2be-6e2077e8e310	d578ad21-d98c-414a-b66a-df86446d4886	0.039	2026-05-09 19:54:16.470757
6d4ad895-d6b5-48fd-b35b-91c3cb83e884	d578ad21-d98c-414a-b66a-df86446d4886	0.015	2026-05-09 13:54:16.470768
f5e48135-8e71-4295-8b8f-c5fbcfaf8c7f	d578ad21-d98c-414a-b66a-df86446d4886	0.01	2026-05-09 07:54:16.470778
071365ef-f105-4232-91e7-ec179ccb8b13	d578ad21-d98c-414a-b66a-df86446d4886	0.031	2026-05-09 01:54:16.47079
65ee4ef5-944a-41fd-bf7b-bd2e86513792	d578ad21-d98c-414a-b66a-df86446d4886	0.018	2026-05-08 19:54:16.4708
bfcb34d7-1d9f-4146-8f3d-d01cf8b660fc	d578ad21-d98c-414a-b66a-df86446d4886	0.02	2026-05-08 13:54:16.470811
fec9bf5a-01fc-47c9-84cc-c4b4be50d8c8	d578ad21-d98c-414a-b66a-df86446d4886	0.008	2026-05-08 07:54:16.470821
09c31054-1ff9-4109-8b51-5af595f26009	d578ad21-d98c-414a-b66a-df86446d4886	0.028	2026-05-08 01:54:16.470832
d01b6e90-dd66-47e4-ac12-cf4dc3e77709	d578ad21-d98c-414a-b66a-df86446d4886	0.035	2026-05-07 19:54:16.470843
06f298a3-b492-4574-80c6-4ffaf4ddc269	d578ad21-d98c-414a-b66a-df86446d4886	0.008	2026-05-07 13:54:16.470854
d27dcd9b-0cc3-4802-954a-e2baa8aaedd2	d578ad21-d98c-414a-b66a-df86446d4886	0.02	2026-05-07 07:54:16.470865
b8a20f77-ebba-4fd1-a28f-7dd7d562b2de	d578ad21-d98c-414a-b66a-df86446d4886	0.018	2026-05-07 01:54:16.470877
f6df67fe-a84c-4c36-ba37-c9f0cdfcb372	d578ad21-d98c-414a-b66a-df86446d4886	0.031	2026-05-06 19:54:16.470887
f586d0be-b748-4f21-882f-dfadeb4f00a2	d578ad21-d98c-414a-b66a-df86446d4886	0.008	2026-05-06 13:54:16.470898
8aa371a2-0c92-4104-8e62-bd2f46ee683e	d578ad21-d98c-414a-b66a-df86446d4886	0.015	2026-05-06 07:54:16.470909
2ea9c30a-4b46-4ad4-9d7e-8ab8537999d2	d578ad21-d98c-414a-b66a-df86446d4886	0.021	2026-05-06 01:54:16.470924
2334172c-f05d-4930-a40f-082f7b5a9be4	d578ad21-d98c-414a-b66a-df86446d4886	0.026	2026-05-05 19:54:16.470935
6a67d944-1fc0-4bb0-87c8-2f794a982a02	d578ad21-d98c-414a-b66a-df86446d4886	0.023	2026-05-05 13:54:16.470945
12505c8c-6697-409c-b77e-e3b106c3c23c	d578ad21-d98c-414a-b66a-df86446d4886	0.015	2026-05-05 07:54:16.470956
f19c8251-23eb-4c97-8a91-a6245e967f74	d578ad21-d98c-414a-b66a-df86446d4886	0.042	2026-05-05 01:54:16.470967
f545915e-ef57-45f6-a03a-5fa6681c53f7	d578ad21-d98c-414a-b66a-df86446d4886	0.045	2026-05-04 19:54:16.470977
9f56ba8b-4b4f-45b4-8171-e6842ec9bfda	d578ad21-d98c-414a-b66a-df86446d4886	0.012	2026-05-04 13:54:16.470987
b824be52-8944-49f4-afcd-5d7e74943bd5	d578ad21-d98c-414a-b66a-df86446d4886	0.009	2026-05-04 07:54:16.470998
90d95a6c-215c-4d1f-bafd-125bbcba9817	d578ad21-d98c-414a-b66a-df86446d4886	0.014	2026-05-04 01:54:16.47101
238e99b3-25a2-4d0f-a8ab-b72cbd042c42	d578ad21-d98c-414a-b66a-df86446d4886	0.034	2026-05-03 19:54:16.471021
cb40856f-2514-47bd-8475-2c1031488b5b	d578ad21-d98c-414a-b66a-df86446d4886	0.028	2026-05-03 13:54:16.471031
f5ee9e75-1f4e-428c-96c5-c34e8b92cf1e	d578ad21-d98c-414a-b66a-df86446d4886	0.014	2026-05-03 07:54:16.471042
25b17f7a-a423-436a-a7f8-da745d287ed3	d578ad21-d98c-414a-b66a-df86446d4886	0.038	2026-05-03 01:54:16.471054
8f60725d-9fd8-466a-ab64-bd5779ab92e7	d578ad21-d98c-414a-b66a-df86446d4886	0.043	2026-05-02 19:54:16.471065
ba8fb079-2d67-40f7-bd63-19b03b7ea436	d578ad21-d98c-414a-b66a-df86446d4886	0.021	2026-05-02 13:54:16.471076
5bdc72c3-eaf4-48aa-9dfd-712a3fdead4f	d578ad21-d98c-414a-b66a-df86446d4886	0.023	2026-05-02 07:54:16.471088
2dbf55d1-7e54-4b22-ac56-867665aae87f	d578ad21-d98c-414a-b66a-df86446d4886	0.05	2026-05-02 01:54:16.4711
5c6882cc-1592-4d21-9246-ca0631a9ce31	d578ad21-d98c-414a-b66a-df86446d4886	0.021	2026-05-01 19:54:16.471111
49804dd2-3b19-42bf-a1b4-3329faff4bb6	d578ad21-d98c-414a-b66a-df86446d4886	0.007	2026-05-01 13:54:16.471123
0ebeaf5e-69e4-430b-a40a-fde2fed359cb	d578ad21-d98c-414a-b66a-df86446d4886	0.01	2026-05-01 07:54:16.471134
902b8df9-6a63-4449-977a-1ef64937494e	d578ad21-d98c-414a-b66a-df86446d4886	0.018	2026-05-01 01:54:16.471145
f7c01d07-21d0-42aa-8c94-1e47cafd264d	d578ad21-d98c-414a-b66a-df86446d4886	0.039	2026-04-30 19:54:16.471157
3b290c2c-aeec-4d8f-b19a-4d6719689bce	d578ad21-d98c-414a-b66a-df86446d4886	0.019	2026-04-30 13:54:16.471168
eb0b22a4-d713-4c91-8d41-9e96bf080293	d578ad21-d98c-414a-b66a-df86446d4886	0.012	2026-04-30 07:54:16.471179
fdfce978-acfe-49d1-81e3-8024d4428cbf	d578ad21-d98c-414a-b66a-df86446d4886	0.04	2026-04-30 01:54:16.47119
ad7f997d-8265-4308-83b0-fbcde4a454f4	d578ad21-d98c-414a-b66a-df86446d4886	0.043	2026-04-29 19:54:16.471201
67f2e6ec-c379-414c-ac8f-45430984233f	d578ad21-d98c-414a-b66a-df86446d4886	0.011	2026-04-29 13:54:16.471213
7bdca463-5b9d-4cd0-a696-52ce47f151d8	d578ad21-d98c-414a-b66a-df86446d4886	0.02	2026-04-29 07:54:16.471223
3368350c-ed6e-4194-9047-26941f345906	d578ad21-d98c-414a-b66a-df86446d4886	0.042	2026-04-29 01:54:16.471234
2390d590-b7a0-4aff-a7fe-4d790aa14b20	d578ad21-d98c-414a-b66a-df86446d4886	0.017	2026-04-28 19:54:16.471245
07212115-7040-466d-86e3-d16ba21c8ea7	d578ad21-d98c-414a-b66a-df86446d4886	0.024	2026-04-28 13:54:16.471256
4605236b-39c2-4dd6-846e-68790ae3a49c	d578ad21-d98c-414a-b66a-df86446d4886	0.027	2026-04-28 07:54:16.471269
81904a0c-3cd3-4f6f-a5c8-e5f0da37dd21	d578ad21-d98c-414a-b66a-df86446d4886	0.017	2026-04-28 01:54:16.471281
c30dd24c-1463-4683-a10c-77e5e924dda5	d578ad21-d98c-414a-b66a-df86446d4886	0.014	2026-04-27 19:54:16.471291
c2c88cef-876c-423a-917a-5c013eb5735b	d578ad21-d98c-414a-b66a-df86446d4886	0.014	2026-04-27 13:54:16.471303
8e50fc5b-4206-4339-b74a-c79ec8a4f2d1	d578ad21-d98c-414a-b66a-df86446d4886	0.021	2026-04-27 07:54:16.471314
408ba1ae-011f-4f23-a897-eccb08b38d54	d578ad21-d98c-414a-b66a-df86446d4886	0.05	2026-04-27 01:54:16.471325
95fac29c-4620-43c5-b2ef-5f6c266351ed	d578ad21-d98c-414a-b66a-df86446d4886	0.028	2026-04-26 19:54:16.471336
559e2d0e-0bb2-4301-8ff6-dcfabde5e447	d578ad21-d98c-414a-b66a-df86446d4886	0.022	2026-04-26 13:54:16.471347
7d8105c2-c1de-44f4-9e2e-4dea0677630d	d578ad21-d98c-414a-b66a-df86446d4886	0.009	2026-04-26 07:54:16.471358
6f7b739a-2554-4337-afbc-138e5823c552	d578ad21-d98c-414a-b66a-df86446d4886	0.04	2026-04-26 01:54:16.471369
96562178-1d3d-4669-bece-4c0e5f0f1722	d578ad21-d98c-414a-b66a-df86446d4886	0.037	2026-04-25 19:54:16.47138
ee8cf6a0-adef-486b-805b-b0cad48956ef	d578ad21-d98c-414a-b66a-df86446d4886	0.009	2026-04-25 13:54:16.471391
c2e98dcc-c464-4c95-a081-58a63053b797	d578ad21-d98c-414a-b66a-df86446d4886	0.023	2026-04-25 07:54:16.471401
7d3fa028-454d-4bd3-a7a2-a1c17b5b7cb4	d578ad21-d98c-414a-b66a-df86446d4886	0.046	2026-04-25 01:54:16.471413
717ced66-c99d-494f-a557-8db52c201721	d578ad21-d98c-414a-b66a-df86446d4886	0.036	2026-04-24 19:54:16.471424
b7a254d7-822d-4081-ad75-cd6c4dfc1d76	d578ad21-d98c-414a-b66a-df86446d4886	0.01	2026-04-24 13:54:16.471435
1bf459a0-eb52-4157-a6de-c4878504ce0b	d578ad21-d98c-414a-b66a-df86446d4886	0.028	2026-04-24 07:54:16.471447
80bea6ca-0fd7-4998-9013-648de46f64e6	d578ad21-d98c-414a-b66a-df86446d4886	0.044	2026-04-24 01:54:16.471458
94aa8425-ee33-49c4-9785-76a9e4e82a02	d578ad21-d98c-414a-b66a-df86446d4886	0.027	2026-04-23 19:54:16.471469
85b48ad7-8d8e-47fd-ad68-1cc990a5f56d	d578ad21-d98c-414a-b66a-df86446d4886	0.016	2026-04-23 13:54:16.47148
ead7b5a2-f60d-4d5f-8239-0c59728936c8	d578ad21-d98c-414a-b66a-df86446d4886	0.015	2026-04-23 07:54:16.471491
52a2dacf-b90b-4f21-a884-49062610875c	d578ad21-d98c-414a-b66a-df86446d4886	0.033	2026-04-23 01:54:16.471502
f6840c62-4210-497a-a3dd-a099bc8380b7	d578ad21-d98c-414a-b66a-df86446d4886	0.026	2026-04-22 19:54:16.471512
fbb2d377-9030-4818-a7d1-646d98ba8b80	d578ad21-d98c-414a-b66a-df86446d4886	0.025	2026-04-22 13:54:16.471525
4d644def-80ea-42dc-bda1-26d203a2fd75	d578ad21-d98c-414a-b66a-df86446d4886	0.024	2026-04-22 07:54:16.471562
eab6abb2-5369-4dad-9376-e7e53d7006a6	d578ad21-d98c-414a-b66a-df86446d4886	0.017	2026-04-22 01:54:16.471573
430a92d8-5c82-46f0-964e-43f881c74149	d578ad21-d98c-414a-b66a-df86446d4886	0.05	2026-04-21 19:54:16.471586
877bbc5f-c960-4cab-82a7-df9bcb021083	d578ad21-d98c-414a-b66a-df86446d4886	0.02	2026-04-21 13:54:16.471597
b78c3a6d-1b9b-4305-8f4c-e2fcbd7a0442	d578ad21-d98c-414a-b66a-df86446d4886	0.024	2026-04-21 07:54:16.47161
1d9655d5-96d9-4800-a749-1794edf0a1fe	d578ad21-d98c-414a-b66a-df86446d4886	0.041	2026-04-21 01:54:16.471621
53458c69-153b-43c5-907b-19497ccff837	d578ad21-d98c-414a-b66a-df86446d4886	0.03	2026-04-20 19:54:16.471632
09d3ad8a-0256-4678-aead-c44dd3159a69	d578ad21-d98c-414a-b66a-df86446d4886	0.022	2026-04-20 13:54:16.471644
77e45b3f-5750-4ae4-9fec-b22c03d0df08	d578ad21-d98c-414a-b66a-df86446d4886	0.027	2026-04-20 07:54:16.471655
a1dfac4b-b34d-4d64-85f8-6157023d5d63	d578ad21-d98c-414a-b66a-df86446d4886	0.024	2026-04-20 01:54:16.471688
67753a0c-6bb8-4e31-9958-6c8cfd0b7693	d578ad21-d98c-414a-b66a-df86446d4886	0.045	2026-04-19 19:54:16.471706
5f2b8386-3af6-4d9b-83bb-d6f277ce5fcf	d578ad21-d98c-414a-b66a-df86446d4886	0.018	2026-04-19 13:54:16.471718
a14987d5-4d4c-4b0a-820d-ec1b646fe281	d578ad21-d98c-414a-b66a-df86446d4886	0.017	2026-04-19 07:54:16.471732
d5a0edbb-6ec8-44a6-ba88-9e3fd0c96011	d578ad21-d98c-414a-b66a-df86446d4886	0.03	2026-04-19 01:54:16.471745
1ba4e1cd-8c53-4dc8-b708-f0f2113ae751	d578ad21-d98c-414a-b66a-df86446d4886	0.042	2026-04-18 19:54:16.471756
8a791bd8-84d3-40bb-aa55-1f284914bd68	d578ad21-d98c-414a-b66a-df86446d4886	0.013	2026-04-18 13:54:16.471768
3b930630-155e-4065-b827-36734182d260	d578ad21-d98c-414a-b66a-df86446d4886	0.025	2026-04-18 07:54:16.471781
d96464ae-7710-4962-84c6-e9590e0fb028	d578ad21-d98c-414a-b66a-df86446d4886	0.045	2026-04-18 01:54:16.471795
6e53b56e-52a7-472c-92ae-f50c495e7e28	d578ad21-d98c-414a-b66a-df86446d4886	0.016	2026-04-17 19:54:16.471834
014e00ee-4b92-410d-aeb6-5a8a1bada136	d578ad21-d98c-414a-b66a-df86446d4886	0.026	2026-04-17 13:54:16.471873
79ecbea4-b4e9-4e11-8f89-3a56badb4c23	d578ad21-d98c-414a-b66a-df86446d4886	0.012	2026-04-17 07:54:16.471892
9ad8bff5-65e6-4a31-ada1-4986100c5561	d578ad21-d98c-414a-b66a-df86446d4886	0.031	2026-04-17 01:54:16.471908
724250ff-a88b-4fe7-9e39-84de2086f168	d578ad21-d98c-414a-b66a-df86446d4886	0.037	2026-04-16 19:54:16.471922
ad3ac094-c83d-4e12-9f6e-2bf4e67f31ea	d578ad21-d98c-414a-b66a-df86446d4886	0.015	2026-04-16 13:54:16.471936
7a7ba856-0dd3-4ac9-88b1-aafd27949313	d578ad21-d98c-414a-b66a-df86446d4886	0.008	2026-04-16 07:54:16.471948
b8f907cc-1650-4716-859e-7411e589d3ed	d578ad21-d98c-414a-b66a-df86446d4886	0.046	2026-04-16 01:54:16.47196
7d10ebd0-7820-4810-9ee6-7fb81cce6559	d578ad21-d98c-414a-b66a-df86446d4886	0.02	2026-04-15 19:54:16.471972
9c2e2bc0-75e7-408b-853a-15b38b9305fa	d578ad21-d98c-414a-b66a-df86446d4886	0.011	2026-04-15 13:54:16.471986
2ad48fab-3251-4847-b663-5465a8dd4166	d578ad21-d98c-414a-b66a-df86446d4886	0.024	2026-04-15 07:54:16.471998
57d7c93a-3ca2-4ed3-aa4d-d4c912428eac	d578ad21-d98c-414a-b66a-df86446d4886	0.026	2026-04-15 01:54:16.472009
b0273bab-d2eb-4946-be77-871514c56992	d578ad21-d98c-414a-b66a-df86446d4886	0.047	2026-04-14 19:54:16.472021
2507b608-ccef-4d44-a0c0-2e189e65bf76	d578ad21-d98c-414a-b66a-df86446d4886	0.022	2026-04-14 13:54:16.472033
4223ed3c-5618-4db9-ad73-e0475128064f	d578ad21-d98c-414a-b66a-df86446d4886	0.013	2026-04-14 07:54:16.472043
760acf54-0955-4da9-ac86-227eae11a1aa	d578ad21-d98c-414a-b66a-df86446d4886	0.013	2026-04-14 01:54:16.472055
a861a5fa-ce72-421f-80ff-9c238407d71a	d578ad21-d98c-414a-b66a-df86446d4886	0.05	2026-04-13 19:54:16.472066
840d3e6e-7bab-40a6-b3ae-0f4de7fb63d3	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.03	2026-05-13 13:54:16.472078
f618c202-7acc-48f9-9e7a-cc345bac3f4e	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.048	2026-05-13 07:54:16.472091
82de9f6a-03c4-4a3d-b54a-2fcd5574c6f5	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.077	2026-05-13 01:54:16.472103
ac30b9ae-a36e-4685-b6f5-934d4d91bf52	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.091	2026-05-12 19:54:16.472114
0c689ae2-959b-4e3c-ae22-20f5447eabdb	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.047	2026-05-12 13:54:16.472126
9c40c24a-071e-453e-8b57-6b0727e0edf0	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.046	2026-05-12 07:54:16.472138
7755f078-983c-4b0d-83ac-e351ad7855a6	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.078	2026-05-12 01:54:16.47215
3c0312d9-7789-4273-aa83-d05896f7f065	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.093	2026-05-11 19:54:16.472162
fb919751-a677-478f-b0d0-58fdcb142cad	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.031	2026-05-11 13:54:16.472173
79674f89-27a5-417e-83aa-401d2c7d4dc3	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.034	2026-05-11 07:54:16.472183
02bf4af4-1aa5-4f4e-882f-9ce7d91dd9ac	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.088	2026-05-11 01:54:16.472196
020cf22b-2005-4399-975c-e79f4c675829	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.068	2026-05-10 19:54:16.47221
1022081e-37a2-44d7-9566-557780468a09	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.044	2026-05-10 13:54:16.472223
010b2a92-0612-4ccd-944b-667947eed507	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.041	2026-05-10 07:54:16.472236
f2af9ede-c32e-415f-bc2a-926a7760deaf	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.08	2026-05-10 01:54:16.472247
4cd406b3-45da-4d52-863e-22f2d86800de	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.074	2026-05-09 19:54:16.472258
2209dd9a-0313-4c3a-b1e6-77f522c81d03	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.049	2026-05-09 13:54:16.472269
58bfa7fa-8257-4f93-bd5b-8f1fabb66d77	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.037	2026-05-09 07:54:16.472282
ac5af5af-17a2-4964-8d43-0d3de73b75e9	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.089	2026-05-09 01:54:16.472294
3c0dc0d8-1a3f-44e8-b511-3ed4c92760b9	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.066	2026-05-08 19:54:16.472305
ed4046f7-e846-4646-9770-b6374761b854	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.035	2026-05-08 13:54:16.472318
4214b340-8ecf-4af7-8505-c01e13524809	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.031	2026-05-08 07:54:16.472329
10478b1d-ebbf-4a2d-a2aa-273d45ed8862	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.062	2026-05-08 01:54:16.47234
2e235232-169f-4b7c-8cfd-984080d7a8ca	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.058	2026-05-07 19:54:16.472352
d8f31421-1ca2-4f5b-ab74-950ef5aa0e55	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.043	2026-05-07 13:54:16.472366
89161e5e-8372-4c0c-bb2c-4e4a27f181b5	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.049	2026-05-07 07:54:16.472378
0405c82a-bccf-436b-9620-0771a64e31a5	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.062	2026-05-07 01:54:16.47239
fa841e33-a4b3-4ea6-966c-cb8d99b79b16	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.063	2026-05-06 19:54:16.472402
b5a70f4d-aee9-48b3-b4fe-12d56ecf9f8a	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.042	2026-05-06 13:54:16.472414
6c321546-91bd-4b1a-8a06-9ae75cf487b7	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.048	2026-05-06 07:54:16.472425
110ca3a6-9eca-4b71-b88c-3abbec600846	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.103	2026-05-06 01:54:16.472436
d349b73e-f5eb-425b-aaef-b6e19961a24b	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.079	2026-05-05 19:54:16.472447
2f8a9bc6-775b-454c-9647-51bdedce1c31	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.036	2026-05-05 13:54:16.472458
ec2a8974-6495-4951-9c7e-cb71c65abea2	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.031	2026-05-05 07:54:16.47247
1e448b60-3501-432d-a446-0a3b02fc1819	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.062	2026-05-05 01:54:16.472484
9bbcb043-464d-46c3-9122-926248fade91	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.064	2026-05-04 19:54:16.472494
656ae18f-dbcc-4edf-a808-dc9994d6d849	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.033	2026-05-04 13:54:16.472507
6513cdde-9221-42c9-bd2b-f08622eefcbb	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.028	2026-05-04 07:54:16.472519
d88f6d3b-dbf3-4fe9-add2-0db6d0d965e1	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.08	2026-05-04 01:54:16.47253
953cb09a-1c66-4c55-9400-558e86610609	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.066	2026-05-03 19:54:16.472541
a5b69bbe-c02d-4aa8-8e36-5f6d5713e01f	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.055	2026-05-03 13:54:16.472552
f8e59331-96bc-4d66-9a2f-145716c0f0af	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.043	2026-05-03 07:54:16.472563
8c910800-7f90-4541-8117-e110b0a716b2	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.088	2026-05-03 01:54:16.472575
e0d9a747-060c-433a-a307-42c88404a139	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.059	2026-05-02 19:54:16.472586
bc1299e8-abd5-489b-a535-f681c6caa4da	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.052	2026-05-02 13:54:16.472598
d6563147-a8ad-4562-8595-83369f03258c	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.042	2026-05-02 07:54:16.472609
73dd6073-4f94-4fdd-a112-76f8f4045abf	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.097	2026-05-02 01:54:16.47262
2959619d-287f-4b47-aefd-b9564b0b85d4	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.082	2026-05-01 19:54:16.472631
19cbfeb7-c8aa-4f19-a9b1-fa21eab551a3	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.041	2026-05-01 13:54:16.472643
63663a15-340a-4137-a350-de5b40f17d17	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.04	2026-05-01 07:54:16.472655
454bbe7b-0130-41bb-b33a-ac16fa04f365	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.062	2026-05-01 01:54:16.472667
becea4dd-0c4c-4e9b-b388-1a52a52e1ac6	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.055	2026-04-30 19:54:16.472677
06c79a8f-c1f7-4cc1-b46c-b39f90e0c1a2	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.054	2026-04-30 13:54:16.47269
58380a90-9ed2-40b6-81ed-707882ff5d34	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.041	2026-04-30 07:54:16.472701
9641320c-5213-4a37-9b11-ed2f062971fc	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.095	2026-04-30 01:54:16.472714
b4403b3d-f50f-4753-9b8a-94cad284d953	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.073	2026-04-29 19:54:16.472725
361d06e3-6370-47ba-8abf-0bd8786fc038	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.03	2026-04-29 13:54:16.472736
5349741f-7dfc-4c7f-9b4e-b6499bf2e277	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.046	2026-04-29 07:54:16.472747
d14813d8-0a04-425c-87d9-6fc0fb195f04	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.055	2026-04-29 01:54:16.472758
a53b410c-252e-4776-a9f2-8fabbbe056e5	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.06	2026-04-28 19:54:16.47277
1fc1f441-96b3-4e96-aee7-dc5041f316d0	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.044	2026-04-28 13:54:16.472781
762a6ad2-2631-42e3-9fce-02817247ee7b	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.037	2026-04-28 07:54:16.472792
248610e1-dd6d-4880-a35f-c1531e511431	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.104	2026-04-28 01:54:16.472803
6f3f7c8a-304e-4328-8af9-0ffe9d8b09f6	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.058	2026-04-27 19:54:16.472814
18c9a054-4c4a-4d2a-b6b3-ebba82a2680f	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.049	2026-04-27 13:54:16.472825
a45f0176-8ca5-40c8-b419-8c87c1fb4012	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.045	2026-04-27 07:54:16.472836
a9aaba4b-12e0-4850-8698-285174462fbf	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.093	2026-04-27 01:54:16.472847
711d033c-0176-40f9-bc07-7e6eaa7e7e3e	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.064	2026-04-26 19:54:16.472858
c81a71af-052d-4643-92c9-10abd6f1b8bf	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.043	2026-04-26 13:54:16.472869
43c90dfd-1804-4be1-9697-9136c6995f98	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.041	2026-04-26 07:54:16.472882
e8b1a38a-8291-43b7-8af8-d3bddbd30548	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.075	2026-04-26 01:54:16.472893
290c9406-9b2d-4af2-99b1-3d3eac5cc7df	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.097	2026-04-25 19:54:16.472905
9e653ad3-6841-4a68-9073-51d4cb846226	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.056	2026-04-25 13:54:16.472916
9593ff56-6c03-456c-aa11-6d330a6a1753	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.037	2026-04-25 07:54:16.472927
8e291d40-7c8e-4651-9ce8-57bd2039b86d	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.084	2026-04-25 01:54:16.473004
1b6f8ca6-58ba-476a-89b4-72a67338c067	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.084	2026-04-24 19:54:16.473016
655d774f-d8bb-45ca-aa2b-f35eb7fe0eb6	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.049	2026-04-24 13:54:16.473028
cf280797-547b-4597-b994-28b72a7f0ad7	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.055	2026-04-24 07:54:16.47304
4ad93324-21cd-49f5-a393-0b3fc5256366	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.063	2026-04-24 01:54:16.47305
d8315b96-d785-4357-9bd7-38123e8aefe4	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.063	2026-04-23 19:54:16.473061
1febb73a-172a-4332-b400-9776e785ce53	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.046	2026-04-23 13:54:16.473072
34e4cfa0-f5e8-4be6-9a04-0f287c3f5705	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.032	2026-04-23 07:54:16.473084
53f56995-b4f1-4c04-bc44-c8089d01de77	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.061	2026-04-23 01:54:16.473095
a557a4f8-bd78-48dc-a5ed-43b091d7a337	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.056	2026-04-22 19:54:16.47311
a28152bf-75b0-4d0a-9602-8a354cc8e09a	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.028	2026-04-22 13:54:16.473122
2d0e7a74-fc25-4b39-9a38-8edc578ea837	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.041	2026-04-22 07:54:16.473134
71af8d61-2de3-4091-b2ff-945653f35d83	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.083	2026-04-22 01:54:16.473147
23c79d2d-98d7-420a-9561-cb292fbf9e43	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.067	2026-04-21 19:54:16.473158
2473bf1c-bb5f-4568-8f63-baba9ba6d429	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.034	2026-04-21 13:54:16.473169
69a01e09-11f0-4dd8-b17f-389b27f2c808	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.048	2026-04-21 07:54:16.47318
e406cb09-1b39-4841-8cec-c21739065da7	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.089	2026-04-21 01:54:16.473193
44858c77-00a6-4bb9-8be3-96f43a66e295	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.076	2026-04-20 19:54:16.473204
d38e8846-a9a4-4610-a4ee-1bede35cfd68	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.047	2026-04-20 13:54:16.473216
42ca9c91-9bf4-437e-8b65-a82d9a3e4c90	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.054	2026-04-20 07:54:16.473227
317044a2-fcb5-4ca9-8758-6d3c143f3054	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.093	2026-04-20 01:54:16.473237
8810d8a8-3fe8-4eb3-92a2-70deec602d94	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.085	2026-04-19 19:54:16.473249
6f94b06b-c33b-4ccf-b7af-956e76f82cc2	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.047	2026-04-19 13:54:16.473261
2764ce66-1ab5-44de-b4b9-d65269060611	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.054	2026-04-19 07:54:16.473273
1eddf8e3-e37b-482e-bf87-48e14cf69d9c	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.074	2026-04-19 01:54:16.473284
8a4c3dd0-0778-4b76-884c-fa70c9726b43	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.08	2026-04-18 19:54:16.473295
226b450e-49c5-4918-8fae-ce8992f030a7	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.046	2026-04-18 13:54:16.473306
26b70649-2abc-4c3b-895e-90d9b0904705	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.053	2026-04-18 07:54:16.473318
bfb0dbfb-8350-4491-b2f8-84120a45e824	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.095	2026-04-18 01:54:16.473329
d050d07e-5b8f-42bc-b95c-3ac8330e95fb	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.056	2026-04-17 19:54:16.473341
187b9f63-48f8-4270-93ee-d42279078dce	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.033	2026-04-17 13:54:16.473352
a35a19a6-496a-40ff-8f81-4bdcedc1e51b	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.037	2026-04-17 07:54:16.473364
83651933-2e22-4195-bf6d-c4ec330f36de	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.091	2026-04-17 01:54:16.473375
145a6cf9-7632-4b31-819e-4768903eeb6c	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.082	2026-04-16 19:54:16.473385
87dbf88c-b36b-42e6-a014-8dbc202cfbae	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.036	2026-04-16 13:54:16.473398
1e55633b-c836-4f0a-9437-d6e126aa5aa1	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.031	2026-04-16 07:54:16.473409
8bc340de-5e64-4e14-82ab-7a65898bf047	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.088	2026-04-16 01:54:16.47342
e44db6ba-a49d-4411-b147-fbd61935126b	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.088	2026-04-15 19:54:16.473431
48fe4428-c8e9-4a8e-a26c-5e65e568c46f	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.054	2026-04-15 13:54:16.473442
2c2718e2-83a8-4814-959f-a52d365dfdea	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.042	2026-04-15 07:54:16.473452
e698a410-aff5-406a-bea5-a029a50238d1	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.078	2026-04-15 01:54:16.473463
f326cf28-afcf-43d2-81e9-0c703294883e	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.056	2026-04-14 19:54:16.473473
7d826518-f326-4891-b301-ba5fda37b282	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.029	2026-04-14 13:54:16.473484
5009a672-4ad8-4fc6-a50d-74d1187054e5	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.04	2026-04-14 07:54:16.473495
7879d2a9-bcfd-4d24-bb13-ab4a9a12ccc3	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.069	2026-04-14 01:54:16.473506
d63655a3-a9f2-4a88-8726-e5179d1ed2e4	eb2dc712-7b4f-4c82-acf2-e88fa0352797	0.065	2026-04-13 19:54:16.473517
c0e1b626-096d-409d-8ff0-5eb56621d3e2	c966ee3a-02cb-4732-96da-2554b55f8535	0.535	2026-05-13 13:54:16.473528
4ab920a8-6b40-4997-94dd-634702d2005a	c966ee3a-02cb-4732-96da-2554b55f8535	0.961	2026-05-13 07:54:16.473542
8fd11442-14b1-492e-875f-413f4ad8ce5c	c966ee3a-02cb-4732-96da-2554b55f8535	1.671	2026-05-13 01:54:16.473555
91f1b096-3f82-4212-94ca-a808adfa6547	c966ee3a-02cb-4732-96da-2554b55f8535	1.433	2026-05-12 19:54:16.473568
cc022c6d-2b71-437a-b62a-962cddafe7c5	c966ee3a-02cb-4732-96da-2554b55f8535	0.956	2026-05-12 13:54:16.473579
5b8cca6a-5b72-4644-a3a0-3de076bd199b	c966ee3a-02cb-4732-96da-2554b55f8535	0.98	2026-05-12 07:54:16.473591
ffd240dd-38c0-468e-a552-8a0c67229249	c966ee3a-02cb-4732-96da-2554b55f8535	1.522	2026-05-12 01:54:16.473603
f3a75316-cc60-41bd-8f04-93bd1aab14a6	c966ee3a-02cb-4732-96da-2554b55f8535	1.155	2026-05-11 19:54:16.473614
0d9837df-f55e-49dc-8c3a-773003ce916c	c966ee3a-02cb-4732-96da-2554b55f8535	0.51	2026-05-11 13:54:16.473625
ba3ebc0c-dfd7-4990-833c-c2b18f811564	c966ee3a-02cb-4732-96da-2554b55f8535	0.861	2026-05-11 07:54:16.473635
6f95cdb1-199b-4dec-a093-5b6da4f732ba	c966ee3a-02cb-4732-96da-2554b55f8535	1.338	2026-05-11 01:54:16.473646
bedf64ef-30cb-400a-a127-e31e6358d199	c966ee3a-02cb-4732-96da-2554b55f8535	1.503	2026-05-10 19:54:16.473657
81970a77-6020-49fd-a31a-ded3916216b2	c966ee3a-02cb-4732-96da-2554b55f8535	0.939	2026-05-10 13:54:16.473669
caad8ef8-d104-4eb6-87c4-a6ed019cea5f	c966ee3a-02cb-4732-96da-2554b55f8535	0.579	2026-05-10 07:54:16.473679
e59a6da8-fb80-431b-be75-58bc86a4f0ea	c966ee3a-02cb-4732-96da-2554b55f8535	1.443	2026-05-10 01:54:16.47369
2895ea10-a6a0-4207-96a1-3f9b20de43cd	c966ee3a-02cb-4732-96da-2554b55f8535	1.488	2026-05-09 19:54:16.473701
0e1fc472-c350-4dd2-bf0b-99e6d0561422	c966ee3a-02cb-4732-96da-2554b55f8535	0.731	2026-05-09 13:54:16.473713
9b425778-932a-4eeb-bfd6-087e1e1cd6ec	c966ee3a-02cb-4732-96da-2554b55f8535	0.535	2026-05-09 07:54:16.473724
24ea3fae-f468-4b64-b90d-a7888d4b8814	c966ee3a-02cb-4732-96da-2554b55f8535	1.227	2026-05-09 01:54:16.473735
c01cf624-fa58-4b9c-956f-3e5e7f66fd56	c966ee3a-02cb-4732-96da-2554b55f8535	1.213	2026-05-08 19:54:16.473747
7583e12b-2bc7-4519-9328-84895b469272	c966ee3a-02cb-4732-96da-2554b55f8535	0.818	2026-05-08 13:54:16.473757
15928312-fcec-4858-9077-8d1957ce56ff	c966ee3a-02cb-4732-96da-2554b55f8535	0.91	2026-05-08 07:54:16.473768
81a4ac70-7d9f-46d9-9dbf-2819652ca0ca	c966ee3a-02cb-4732-96da-2554b55f8535	1.21	2026-05-08 01:54:16.473778
b632f659-ebd0-44e4-86fa-53d1957ff21a	c966ee3a-02cb-4732-96da-2554b55f8535	1.541	2026-05-07 19:54:16.47379
d80383b6-8f60-4c16-8051-a78e3acbd94d	c966ee3a-02cb-4732-96da-2554b55f8535	0.631	2026-05-07 13:54:16.473801
ef14f85b-358d-44d1-9818-5403b911b974	c966ee3a-02cb-4732-96da-2554b55f8535	0.953	2026-05-07 07:54:16.473813
c5fa34b9-96d7-45ae-bf95-125f1754f9b1	c966ee3a-02cb-4732-96da-2554b55f8535	1.65	2026-05-07 01:54:16.473824
e67f7ea2-04f9-41ef-9cc0-94a650a2bb62	c966ee3a-02cb-4732-96da-2554b55f8535	1.411	2026-05-06 19:54:16.473834
f1248016-0b0d-4890-9334-aa5f89e3f08f	c966ee3a-02cb-4732-96da-2554b55f8535	0.713	2026-05-06 13:54:16.473846
bb041dd4-649a-4bdb-a292-238f619accec	c966ee3a-02cb-4732-96da-2554b55f8535	0.644	2026-05-06 07:54:16.473857
cbaef1ef-74f3-4ee0-a42d-97d43004ae9b	c966ee3a-02cb-4732-96da-2554b55f8535	1.204	2026-05-06 01:54:16.473869
4c4fc3f3-2ce7-4aaf-8c50-57a843606580	c966ee3a-02cb-4732-96da-2554b55f8535	1.793	2026-05-05 19:54:16.473879
4b6c039a-e361-4554-902f-13e10ff77f6f	c966ee3a-02cb-4732-96da-2554b55f8535	0.688	2026-05-05 13:54:16.473889
fd84c2f3-a9c6-45cd-9ba0-832fd2bc220f	c966ee3a-02cb-4732-96da-2554b55f8535	0.742	2026-05-05 07:54:16.4739
a644fbf8-d5e8-4600-a16a-dfdaa25f4842	c966ee3a-02cb-4732-96da-2554b55f8535	1.809	2026-05-05 01:54:16.47391
1cd27554-b5dd-48cc-935d-7f8d27304d06	c966ee3a-02cb-4732-96da-2554b55f8535	1.508	2026-05-04 19:54:16.47392
fc3e04c1-9b1c-4f32-9004-7a4700d5c4e7	c966ee3a-02cb-4732-96da-2554b55f8535	0.756	2026-05-04 13:54:16.473931
b6af93ce-a0e9-440f-aaeb-99cee495fa5f	c966ee3a-02cb-4732-96da-2554b55f8535	0.692	2026-05-04 07:54:16.473942
36f43629-b0b9-40ce-9fee-05b0f8b77a5b	c966ee3a-02cb-4732-96da-2554b55f8535	1.081	2026-05-04 01:54:16.473953
3e72a9db-60f5-4ae7-94a4-4e56e020345b	c966ee3a-02cb-4732-96da-2554b55f8535	1.239	2026-05-03 19:54:16.473964
bd75c23d-c251-48ec-b287-ee8ff1b30b09	c966ee3a-02cb-4732-96da-2554b55f8535	0.861	2026-05-03 13:54:16.473975
622fcdca-9315-43ae-8c0b-9cd41ad0bc5a	c966ee3a-02cb-4732-96da-2554b55f8535	0.796	2026-05-03 07:54:16.473987
ad37fd68-89be-42e7-b508-1d2f6527c51a	c966ee3a-02cb-4732-96da-2554b55f8535	1.602	2026-05-03 01:54:16.473999
bb07d02a-7349-451c-85ee-0b0226f8f094	c966ee3a-02cb-4732-96da-2554b55f8535	1.095	2026-05-02 19:54:16.47401
aab4eadd-98f7-4898-921e-1002a2d7cb02	c966ee3a-02cb-4732-96da-2554b55f8535	0.759	2026-05-02 13:54:16.474022
2a9faf30-7115-4adf-abf0-ba0b563232c4	c966ee3a-02cb-4732-96da-2554b55f8535	0.945	2026-05-02 07:54:16.474033
17b1468f-ba8b-4578-952c-115304253781	c966ee3a-02cb-4732-96da-2554b55f8535	1.309	2026-05-02 01:54:16.474044
c1383a54-0703-4372-9920-ff0770272bfa	c966ee3a-02cb-4732-96da-2554b55f8535	1.545	2026-05-01 19:54:16.474055
08d07b12-7560-4379-99c1-592f7b489601	c966ee3a-02cb-4732-96da-2554b55f8535	0.549	2026-05-01 13:54:16.474066
482b93a5-9f97-4d73-b660-90c135da4df2	c966ee3a-02cb-4732-96da-2554b55f8535	0.967	2026-05-01 07:54:16.474077
c694265f-c1d5-4cea-b45d-2cd3e72cdd5b	c966ee3a-02cb-4732-96da-2554b55f8535	1.464	2026-05-01 01:54:16.474088
2bd07ab8-c3c6-46d2-beb5-bd2f62d976d1	c966ee3a-02cb-4732-96da-2554b55f8535	1.128	2026-04-30 19:54:16.474098
e41fd3b3-7c60-46a3-a9a5-98756bb7a042	c966ee3a-02cb-4732-96da-2554b55f8535	0.568	2026-04-30 13:54:16.474109
34aad57f-fd59-4881-93ec-d786c655d18e	c966ee3a-02cb-4732-96da-2554b55f8535	0.76	2026-04-30 07:54:16.474121
93384dc0-ed95-4a9d-859f-d0199eab8b33	c966ee3a-02cb-4732-96da-2554b55f8535	1.413	2026-04-30 01:54:16.474132
421a02fc-0645-4bce-96f4-a9095765497a	c966ee3a-02cb-4732-96da-2554b55f8535	0.995	2026-04-29 19:54:16.474143
fd75180e-4700-4ae5-9a30-541f350470a0	c966ee3a-02cb-4732-96da-2554b55f8535	0.976	2026-04-29 13:54:16.474154
0973c5b8-4435-4aff-9431-ba2d91304050	c966ee3a-02cb-4732-96da-2554b55f8535	0.937	2026-04-29 07:54:16.474165
3d63b537-b40e-4b90-a1a8-6884c39155c4	c966ee3a-02cb-4732-96da-2554b55f8535	1.33	2026-04-29 01:54:16.474175
3ccae8b2-8d34-4ebc-98f9-ab1f2bd403fa	c966ee3a-02cb-4732-96da-2554b55f8535	1.017	2026-04-28 19:54:16.474186
d7879bd6-72e0-4d86-9f3b-f01b6e7c8d6a	c966ee3a-02cb-4732-96da-2554b55f8535	0.898	2026-04-28 13:54:16.474199
f6bfb67f-238a-4570-af3a-2b62f918d391	c966ee3a-02cb-4732-96da-2554b55f8535	0.734	2026-04-28 07:54:16.474212
3924f9ff-b31e-488c-b090-2f44547c13d5	c966ee3a-02cb-4732-96da-2554b55f8535	1.562	2026-04-28 01:54:16.474223
34c58d50-4e93-4bc1-bf17-f86803d49b9d	c966ee3a-02cb-4732-96da-2554b55f8535	1.373	2026-04-27 19:54:16.474235
e6cbad05-b266-4df5-af34-845b8b85d75f	c966ee3a-02cb-4732-96da-2554b55f8535	0.624	2026-04-27 13:54:16.474246
9ca5dfa0-bc57-489f-818f-c8c05c586358	c966ee3a-02cb-4732-96da-2554b55f8535	0.899	2026-04-27 07:54:16.474256
d0dd53d0-4a38-42a2-8ce4-ae3a2de37dae	c966ee3a-02cb-4732-96da-2554b55f8535	1.802	2026-04-27 01:54:16.474268
aaabcda5-6dfa-4ae4-a8b8-1fe5afcf585d	c966ee3a-02cb-4732-96da-2554b55f8535	1.132	2026-04-26 19:54:16.47428
28af6165-82ac-4aea-9f9b-e98c34756d07	c966ee3a-02cb-4732-96da-2554b55f8535	0.76	2026-04-26 13:54:16.474292
db7368ea-69c3-4a2c-9c2d-b64c2c95882d	c966ee3a-02cb-4732-96da-2554b55f8535	0.678	2026-04-26 07:54:16.474303
99c71250-e619-48cb-b084-fd030ef12fdc	c966ee3a-02cb-4732-96da-2554b55f8535	1.749	2026-04-26 01:54:16.474314
89026741-baed-4374-9c8d-4574f3355bc1	c966ee3a-02cb-4732-96da-2554b55f8535	1.372	2026-04-25 19:54:16.474325
53de4ec2-da31-45d6-afa4-59d7fd9044ff	c966ee3a-02cb-4732-96da-2554b55f8535	0.921	2026-04-25 13:54:16.474336
13d65052-1dc2-4490-9133-22af01bceee9	c966ee3a-02cb-4732-96da-2554b55f8535	0.913	2026-04-25 07:54:16.474347
406a9523-1054-4c90-a90b-9659478887e7	c966ee3a-02cb-4732-96da-2554b55f8535	1.161	2026-04-25 01:54:16.474358
8ffb3c9c-3978-4832-9d78-39e046a0ab61	c966ee3a-02cb-4732-96da-2554b55f8535	1.629	2026-04-24 19:54:16.47437
916cbe01-7c61-4892-99c0-0428375ba0e4	c966ee3a-02cb-4732-96da-2554b55f8535	0.693	2026-04-24 13:54:16.474381
b9f9deeb-af73-44ed-8154-bb7def06c71a	c966ee3a-02cb-4732-96da-2554b55f8535	0.948	2026-04-24 07:54:16.474392
21cdf04a-6e4c-445f-82e1-d69d1d8ee24e	c966ee3a-02cb-4732-96da-2554b55f8535	1.372	2026-04-24 01:54:16.474404
6250f983-bfdf-45b4-87b2-5557f8870387	c966ee3a-02cb-4732-96da-2554b55f8535	1.657	2026-04-23 19:54:16.474416
e2613d32-8e99-42cf-b46a-b4d3a9f951de	c966ee3a-02cb-4732-96da-2554b55f8535	0.629	2026-04-23 13:54:16.474428
5a5e012b-4886-43a7-844e-f6ba46c7beef	c966ee3a-02cb-4732-96da-2554b55f8535	0.636	2026-04-23 07:54:16.47444
fedde7b7-4b74-4616-a9ec-dd7678365504	c966ee3a-02cb-4732-96da-2554b55f8535	1.444	2026-04-23 01:54:16.474452
b7cd808f-f727-4dda-b9a6-755cf9963842	c966ee3a-02cb-4732-96da-2554b55f8535	1.819	2026-04-22 19:54:16.474463
c152a632-5e76-4774-9881-49962b91099d	c966ee3a-02cb-4732-96da-2554b55f8535	0.73	2026-04-22 13:54:16.474474
845acc77-e424-44d0-851b-c750a6dfee0b	c966ee3a-02cb-4732-96da-2554b55f8535	0.563	2026-04-22 07:54:16.474485
45b00036-e8f9-4fd2-aa46-47e51956f7a5	c966ee3a-02cb-4732-96da-2554b55f8535	1.4	2026-04-22 01:54:16.474495
da95dfcd-a411-45e0-87a0-724d032621dd	c966ee3a-02cb-4732-96da-2554b55f8535	1.224	2026-04-21 19:54:16.474506
d8c616a2-09a9-49a5-bdfd-9c612ad1a51b	c966ee3a-02cb-4732-96da-2554b55f8535	0.76	2026-04-21 13:54:16.474517
cbf8a2c5-73a0-4244-bded-1f43c3d05282	c966ee3a-02cb-4732-96da-2554b55f8535	0.756	2026-04-21 07:54:16.474531
cd826908-aaa3-4bb4-b3e3-6536c062ce39	c966ee3a-02cb-4732-96da-2554b55f8535	1.324	2026-04-21 01:54:16.474542
67af2552-9ea6-40c3-bb0e-cdec6f0b10ae	c966ee3a-02cb-4732-96da-2554b55f8535	1.203	2026-04-20 19:54:16.474553
d14bf528-2ec9-446b-90e9-11d490bf22c4	c966ee3a-02cb-4732-96da-2554b55f8535	0.582	2026-04-20 13:54:16.474565
a46c7c85-4f11-4c84-8607-355b8dfe7a1d	c966ee3a-02cb-4732-96da-2554b55f8535	0.832	2026-04-20 07:54:16.474576
3bb90b07-4fa2-4c57-9292-1cc7ffe16f81	c966ee3a-02cb-4732-96da-2554b55f8535	1.43	2026-04-20 01:54:16.47459
a9ecc0b0-0ca7-4580-ad89-818274ff42d4	c966ee3a-02cb-4732-96da-2554b55f8535	1.123	2026-04-19 19:54:16.474602
8c551f84-ba77-4787-af43-b8077a3b1376	c966ee3a-02cb-4732-96da-2554b55f8535	0.87	2026-04-19 13:54:16.474615
39e7513c-322c-4482-8023-80d1322ae0f1	c966ee3a-02cb-4732-96da-2554b55f8535	0.511	2026-04-19 07:54:16.474627
a425a3ee-4844-4d08-a8ea-b61084d913b8	c966ee3a-02cb-4732-96da-2554b55f8535	1.588	2026-04-19 01:54:16.474637
cd6d42b8-24f1-486d-ac30-c29b43b8048d	c966ee3a-02cb-4732-96da-2554b55f8535	1.552	2026-04-18 19:54:16.474648
9db6eabe-2b5e-4488-84e1-dea896c60a3c	c966ee3a-02cb-4732-96da-2554b55f8535	0.888	2026-04-18 13:54:16.47466
dd1c2fa2-dda6-4b95-8950-c2851e349b87	c966ee3a-02cb-4732-96da-2554b55f8535	0.679	2026-04-18 07:54:16.474671
1f93cf77-b0a9-45f5-931c-aa1cc4a89399	c966ee3a-02cb-4732-96da-2554b55f8535	1.514	2026-04-18 01:54:16.474682
de073e7a-246b-4fb7-8a6d-812b100d4c79	c966ee3a-02cb-4732-96da-2554b55f8535	1.657	2026-04-17 19:54:16.474694
f1070e12-31b4-476d-a9cd-d3a9a22f0c13	c966ee3a-02cb-4732-96da-2554b55f8535	0.971	2026-04-17 13:54:16.474706
f260e5d9-a8c1-4786-ba31-881614ff1f9f	c966ee3a-02cb-4732-96da-2554b55f8535	0.733	2026-04-17 07:54:16.474717
a45f738d-836b-4bf6-a971-934a54c94b85	c966ee3a-02cb-4732-96da-2554b55f8535	0.944	2026-04-17 01:54:16.474728
9c6cd7bb-09ce-42cb-8beb-fa28ac3b5b6c	c966ee3a-02cb-4732-96da-2554b55f8535	1.367	2026-04-16 19:54:16.474739
42aa324a-1ddf-490f-a4a2-25bf01cdaae5	c966ee3a-02cb-4732-96da-2554b55f8535	0.779	2026-04-16 13:54:16.474757
e046893e-ca1d-4ed2-9079-82358c224373	c966ee3a-02cb-4732-96da-2554b55f8535	0.916	2026-04-16 07:54:16.474769
bbbc5d3c-d03d-4406-9db8-fa2d4a67d3ea	c966ee3a-02cb-4732-96da-2554b55f8535	1.706	2026-04-16 01:54:16.474781
9a714336-579b-4e44-a8c1-5722d8b43f6f	c966ee3a-02cb-4732-96da-2554b55f8535	1.311	2026-04-15 19:54:16.474793
05f0ba1b-01a7-4840-96f2-b7ebb68778ed	c966ee3a-02cb-4732-96da-2554b55f8535	0.748	2026-04-15 13:54:16.474804
e4fb4490-d685-4db3-a79e-182f801ec3dc	c966ee3a-02cb-4732-96da-2554b55f8535	0.714	2026-04-15 07:54:16.474815
9838adb8-92cf-4284-91e9-a6e67523165f	c966ee3a-02cb-4732-96da-2554b55f8535	1.567	2026-04-15 01:54:16.474828
edc7c8b2-0c30-4ce7-8fb6-11fb241e1c8c	c966ee3a-02cb-4732-96da-2554b55f8535	1.283	2026-04-14 19:54:16.474839
b5953b5e-0794-4f43-a61d-bc7a43bb0acb	c966ee3a-02cb-4732-96da-2554b55f8535	0.811	2026-04-14 13:54:16.47485
ca73cea4-c236-4a2b-82bf-e651ff06a468	c966ee3a-02cb-4732-96da-2554b55f8535	0.566	2026-04-14 07:54:16.474862
77f015c4-ee37-43c3-95a2-2886094b9c14	c966ee3a-02cb-4732-96da-2554b55f8535	1.337	2026-04-14 01:54:16.474873
2c17ac62-2215-4803-97fe-55814348aca4	c966ee3a-02cb-4732-96da-2554b55f8535	1.792	2026-04-13 19:54:16.474885
\.


--
-- TOC entry 5110 (class 0 OID 18934)
-- Dependencies: 235
-- Data for Name: home_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.home_users (id, home_id, user_id, role, joined_at) FROM stdin;
11	6fcf9da4-756a-437b-86d5-cc85e0b238a9	e59daddf-b561-4b34-9ad8-a87b1d146aa3	ADMIN	2026-05-11 14:54:16.430933+07
12	6fcf9da4-756a-437b-86d5-cc85e0b238a9	904250f1-49bc-453c-853c-993a590c53b3	MEMBER	2026-05-11 14:54:16.432716+07
13	75d7625d-1a0a-4035-a253-35c7ab438172	3d609779-03cf-4d26-867e-884a818f37cf	ADMIN	2026-05-11 14:54:16.433639+07
14	75d7625d-1a0a-4035-a253-35c7ab438172	904250f1-49bc-453c-853c-993a590c53b3	MEMBER	2026-05-11 14:54:16.434428+07
15	75d7625d-1a0a-4035-a253-35c7ab438172	d9c9b2f0-4ca4-4221-9af1-f70952c5c3da	MEMBER	2026-05-11 14:54:16.435305+07
\.


--
-- TOC entry 5108 (class 0 OID 18927)
-- Dependencies: 233
-- Data for Name: homes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.homes (id, name, address, timezone, is_active, created_at) FROM stdin;
6fcf9da4-756a-437b-86d5-cc85e0b238a9	Nhà Nguyễn Văn Admin	123 Đường Lê Lợi, Quận 1, TP. Hồ Chí Minh	Asia/Ho_Chi_Minh	t	2026-05-11 13:54:16.427404+07
75d7625d-1a0a-4035-a253-35c7ab438172	Biệt thự Phạm Gia	456 Đường Nguyễn Huệ, Quận 3, TP. Hồ Chí Minh	Asia/Ho_Chi_Minh	t	2026-05-11 13:54:16.428697+07
\.


--
-- TOC entry 5120 (class 0 OID 19099)
-- Dependencies: 245
-- Data for Name: password_reset_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.password_reset_tokens (id, user_id, token_hash, expires_at, used_at, created_at) FROM stdin;
\.


--
-- TOC entry 5093 (class 0 OID 18686)
-- Dependencies: 218
-- Data for Name: rooms; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rooms (id, name, icon, image_url, created_at, home_id) FROM stdin;
e84c36cc-eb12-46c2-8d08-d10203de6793	Phòng ngủ chính	bed	\N	2026-05-11 15:54:16.435726+07	6fcf9da4-756a-437b-86d5-cc85e0b238a9
b9a3082e-2497-49f7-bd43-e7a729705f18	Phòng khách	sofa	\N	2026-05-11 15:54:16.437381+07	6fcf9da4-756a-437b-86d5-cc85e0b238a9
95d1fdcc-75c7-4155-b1b2-2c877bcce770	Bếp	kitchen	\N	2026-05-11 15:54:16.437897+07	6fcf9da4-756a-437b-86d5-cc85e0b238a9
81922cb9-60a4-4c70-abb8-55ff18e95097	Nhà vệ sinh	bath	\N	2026-05-11 15:54:16.438337+07	6fcf9da4-756a-437b-86d5-cc85e0b238a9
5f51de5c-b912-4cd5-bd6c-965da8fd021f	Phòng ngủ con	bed	\N	2026-05-11 15:54:16.438782+07	6fcf9da4-756a-437b-86d5-cc85e0b238a9
4bc80010-bebc-4f99-a448-3c1dfae5b8c6	Master Bedroom	bed	\N	2026-05-11 15:54:16.439212+07	75d7625d-1a0a-4035-a253-35c7ab438172
4211dcf2-3b21-4094-9bd4-d3c3ef349f8a	Living Room	sofa	\N	2026-05-11 15:54:16.439639+07	75d7625d-1a0a-4035-a253-35c7ab438172
54f92a97-d460-430a-aef9-9d085e4baebc	Kitchen	kitchen	\N	2026-05-11 15:54:16.440042+07	75d7625d-1a0a-4035-a253-35c7ab438172
d674aec4-2c57-498a-965b-55ce44e9b5d3	Garage	garage	\N	2026-05-11 15:54:16.44045+07	75d7625d-1a0a-4035-a253-35c7ab438172
\.


--
-- TOC entry 5100 (class 0 OID 18776)
-- Dependencies: 225
-- Data for Name: schedules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.schedules (id, device_id, name, "time", days_of_week, action_payload, is_active, source_suggestion_id) FROM stdin;
\.


--
-- TOC entry 5118 (class 0 OID 19071)
-- Dependencies: 243
-- Data for Name: security_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.security_events (id, home_id, event_type, severity, description, "timestamp") FROM stdin;
ef26dd88-4869-48ce-880a-f88f7d23c978	6fcf9da4-756a-437b-86d5-cc85e0b238a9	motion_detected	medium	Phát hiện chuyển động tại phòng khách lúc 2:30 AM	2026-05-13 08:54:16.51125
781439e0-7b3d-4dc1-a02a-867f07d1c53e	6fcf9da4-756a-437b-86d5-cc85e0b238a9	door_opened	low	Cửa chính mở lúc 7:15 AM	2026-05-12 23:54:16.511254
77eba25b-7b03-4e60-b380-e28d5a16f989	6fcf9da4-756a-437b-86d5-cc85e0b238a9	device_offline	low	Đèn nhà tắm mất kết nối	2026-05-13 11:54:16.511255
4a3c429d-a1da-4642-8407-824fc4512820	6fcf9da4-756a-437b-86d5-cc85e0b238a9	unusual_activity	high	Phát hiện hoạt động bất thường: đèn bật nhiều lần ban đêm	2026-05-12 07:54:16.511256
9846e6a3-233a-45a4-a7b7-e1613c6187bd	6fcf9da4-756a-437b-86d5-cc85e0b238a9	motion_detected	high	Phát hiện chuyển động khi không có ai ở nhà (3:00 AM)	2026-05-11 13:54:16.511258
7101c0b9-e2b5-47e5-be8b-4fff3e63b597	6fcf9da4-756a-437b-86d5-cc85e0b238a9	smoke_detected	high	Cảm biến khói phát hiện khói ở bếp	2026-05-10 13:54:16.511259
4691be3f-a97d-4a8c-9a66-59d08938ccb7	6fcf9da4-756a-437b-86d5-cc85e0b238a9	door_opened	medium	Cửa garage mở khi chủ nhà đang ra ngoài	2026-05-09 13:54:16.51126
16d57e72-542d-4a37-be7a-26bd934f2166	6fcf9da4-756a-437b-86d5-cc85e0b238a9	motion_detected	low	Chuyển động phòng khách lúc 8:00 AM (bình thường)	2026-05-08 13:54:16.511261
3b4d6335-5a76-42ad-ab26-9f63a5734d86	75d7625d-1a0a-4035-a253-35c7ab438172	motion_detected	low	Motion detected in Living Room	2026-05-13 07:54:16.511262
913832a0-48ca-43b6-b7c1-bfcf8f903280	75d7625d-1a0a-4035-a253-35c7ab438172	door_opened	medium	Garage door opened at 11 PM	2026-05-13 05:54:16.511262
89742639-9618-4f79-bfdc-b5874768e462	75d7625d-1a0a-4035-a253-35c7ab438172	unusual_activity	medium	Unusual energy consumption detected	2026-05-12 13:54:16.511263
\.


--
-- TOC entry 5101 (class 0 OID 18799)
-- Dependencies: 226
-- Data for Name: sensor_data; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sensor_data ("time", device_id, metric_type, value) FROM stdin;
\.


--
-- TOC entry 5114 (class 0 OID 19008)
-- Dependencies: 239
-- Data for Name: suggestion_decision_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.suggestion_decision_logs (id, pattern_id, home_id, user_id, decision_score, should_suggest, blocked_by, cooldown_signature, metadata_json, created_at) FROM stdin;
\.


--
-- TOC entry 5112 (class 0 OID 18984)
-- Dependencies: 237
-- Data for Name: suggestion_feedback_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.suggestion_feedback_logs (id, suggestion_id, user_id, feedback_type, feedback_reason, feedback_time, created_at) FROM stdin;
1	8	e59daddf-b561-4b34-9ad8-a87b1d146aa3	REJECT	\N	2026-05-13 14:31:38.107786+07	2026-05-13 14:31:38.107786+07
\.


--
-- TOC entry 5107 (class 0 OID 18894)
-- Dependencies: 232
-- Data for Name: suggestion_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.suggestion_logs (id, user_id, pattern_id, action_type, suggestion_text, suggestion_json, was_accepted, created_at) FROM stdin;
6	e59daddf-b561-4b34-9ad8-a87b1d146aa3	\N	SCHEDULE	Bật điều hòa tự động lúc 21:30 thay vì 22:00 vì bạn thường lên phòng lúc 21:45	{"time": "21:30", "action": "on", "device": "Điều hòa Panasonic"}	t	2026-05-13 13:54:16.420134+07
7	e59daddf-b561-4b34-9ad8-a87b1d146aa3	\N	AUTOMATION	Tạo automation tắt đèn sau 30 phút nếu không có chuyển động	{"action": "toggle_off", "trigger": "no_motion", "duration": 1800}	f	2026-05-13 13:54:16.420134+07
9	904250f1-49bc-453c-853c-993a590c53b3	\N	SCHEDULE	Bật đèn phòng khách lúc 18:00 vào các ngày trong tuần	{"days": [0, 1, 2, 3, 4], "time": "18:00", "device": "Đèn trần phòng khách"}	t	2026-05-13 13:54:16.420134+07
10	904250f1-49bc-453c-853c-993a590c53b3	\N	ALERT	Phát hiện thiết bị bật khi không ai ở nhà (11:00 - 15:00)	{"devices": ["Đèn bếp"], "time_range": ["11:00", "15:00"]}	\N	2026-05-13 13:54:16.420134+07
8	e59daddf-b561-4b34-9ad8-a87b1d146aa3	\N	ALERT	Cảnh báo: Điều hòa đã hoạt động liên tục 8 tiếng, có thể do cửa sổ mở	{"device": "Điều hòa Panasonic", "duration": 28800, "action_taken": "DISMISSED"}	f	2026-05-13 13:54:16.420134+07
\.


--
-- TOC entry 5105 (class 0 OID 18866)
-- Dependencies: 230
-- Data for Name: user_patterns; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_patterns (id, user_id, device_id, pattern_type, pattern_data, confidence, computed_at, is_active, home_id) FROM stdin;
\.


--
-- TOC entry 5103 (class 0 OID 18836)
-- Dependencies: 228
-- Data for Name: user_presence; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_presence (id, user_id, room_id, is_home, detected_by, last_seen, home_id) FROM stdin;
\.


--
-- TOC entry 5094 (class 0 OID 18703)
-- Dependencies: 219
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, password_hash, full_name, avatar_url, role, face_encoding, is_active, created_at) FROM stdin;
904250f1-49bc-453c-853c-993a590c53b3	member@demo.local	$2b$12$HNu/gqc09oj11PawbFvXn.1L3y0L8WogXChaAk65T27nvMLr4pHbu	Trần Thị Member	https://ui-avatars.com/api/?name=Member&background=10b981&color=fff	MEMBER	\N	t	2026-05-10 13:54:16.425226+07
d9c9b2f0-4ca4-4221-9af1-f70952c5c3da	guest@demo.local	$2b$12$gMk8aIlXR03zGrm9ZZGWdOqSaCDrJH/BCI5UTr4lEaMWC9C6c9ZSm	Lê Văn Guest	https://ui-avatars.com/api/?name=Guest&background=f59e0b&color=fff	MEMBER	\N	t	2026-05-10 13:54:16.426163+07
3d609779-03cf-4d26-867e-884a818f37cf	owner2@demo.local	$2b$12$GkzWMJqoGEEpxqS29IRgEeJEq6y2lSUBFDk5mLhUsoWM1BUDR.aOq	Phạm Thị Owner	https://ui-avatars.com/api/?name=Owner&background=ef4444&color=fff	ADMIN	\N	t	2026-05-10 13:54:16.42697+07
e59daddf-b561-4b34-9ad8-a87b1d146aa3	admin@gmail.com	$2b$12$xiWdSdV0MzlMJ.P0NbDMn.6J8avMybhnFPhd8vDeJpFXD0FxsQ7UG	Nguyễn Văn Admin	https://ui-avatars.com/api/?name=Admin&background=6366f1&color=fff	ADMIN	\N	t	2026-05-10 13:54:16.4217+07
\.


--
-- TOC entry 5138 (class 0 OID 0)
-- Dependencies: 221
-- Name: activity_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.activity_logs_id_seq', 1, false);


--
-- TOC entry 5139 (class 0 OID 0)
-- Dependencies: 234
-- Name: home_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.home_users_id_seq', 15, true);


--
-- TOC entry 5140 (class 0 OID 0)
-- Dependencies: 224
-- Name: schedules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.schedules_id_seq', 1, false);


--
-- TOC entry 5141 (class 0 OID 0)
-- Dependencies: 238
-- Name: suggestion_decision_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.suggestion_decision_logs_id_seq', 1, false);


--
-- TOC entry 5142 (class 0 OID 0)
-- Dependencies: 236
-- Name: suggestion_feedback_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.suggestion_feedback_logs_id_seq', 1, true);


--
-- TOC entry 5143 (class 0 OID 0)
-- Dependencies: 231
-- Name: suggestion_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.suggestion_logs_id_seq', 10, true);


--
-- TOC entry 5144 (class 0 OID 0)
-- Dependencies: 229
-- Name: user_patterns_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_patterns_id_seq', 1, false);


--
-- TOC entry 5145 (class 0 OID 0)
-- Dependencies: 227
-- Name: user_presence_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_presence_id_seq', 1, false);


--
-- TOC entry 4850 (class 2606 OID 18750)
-- Name: activity_logs activity_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 4837 (class 2606 OID 18685)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 4901 (class 2606 OID 19090)
-- Name: auth_sessions auth_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_sessions
    ADD CONSTRAINT auth_sessions_pkey PRIMARY KEY (id);


--
-- TOC entry 4903 (class 2606 OID 19092)
-- Name: auth_sessions auth_sessions_refresh_token_hash_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_sessions
    ADD CONSTRAINT auth_sessions_refresh_token_hash_key UNIQUE (refresh_token_hash);


--
-- TOC entry 4913 (class 2606 OID 19132)
-- Name: automation_actions automation_actions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.automation_actions
    ADD CONSTRAINT automation_actions_pkey PRIMARY KEY (id);


--
-- TOC entry 4911 (class 2606 OID 19120)
-- Name: automation_conditions automation_conditions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.automation_conditions
    ADD CONSTRAINT automation_conditions_pkey PRIMARY KEY (id);


--
-- TOC entry 4890 (class 2606 OID 19041)
-- Name: automations automations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.automations
    ADD CONSTRAINT automations_pkey PRIMARY KEY (id);


--
-- TOC entry 4892 (class 2606 OID 19053)
-- Name: device_logs device_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.device_logs
    ADD CONSTRAINT device_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 4855 (class 2606 OID 18769)
-- Name: device_states device_states_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.device_states
    ADD CONSTRAINT device_states_pkey PRIMARY KEY (device_id);


--
-- TOC entry 4845 (class 2606 OID 18734)
-- Name: devices devices_mqtt_topic_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_mqtt_topic_key UNIQUE (mqtt_topic);


--
-- TOC entry 4847 (class 2606 OID 18732)
-- Name: devices devices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_pkey PRIMARY KEY (id);


--
-- TOC entry 4895 (class 2606 OID 19064)
-- Name: energy_logs energy_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.energy_logs
    ADD CONSTRAINT energy_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 4875 (class 2606 OID 18940)
-- Name: home_users home_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.home_users
    ADD CONSTRAINT home_users_pkey PRIMARY KEY (id);


--
-- TOC entry 4873 (class 2606 OID 18932)
-- Name: homes homes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.homes
    ADD CONSTRAINT homes_pkey PRIMARY KEY (id);


--
-- TOC entry 4907 (class 2606 OID 19105)
-- Name: password_reset_tokens password_reset_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_pkey PRIMARY KEY (id);


--
-- TOC entry 4909 (class 2606 OID 19107)
-- Name: password_reset_tokens password_reset_tokens_token_hash_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_token_hash_key UNIQUE (token_hash);


--
-- TOC entry 4840 (class 2606 OID 18693)
-- Name: rooms rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_pkey PRIMARY KEY (id);


--
-- TOC entry 4858 (class 2606 OID 18783)
-- Name: schedules schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_pkey PRIMARY KEY (id);


--
-- TOC entry 4899 (class 2606 OID 19077)
-- Name: security_events security_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_events
    ADD CONSTRAINT security_events_pkey PRIMARY KEY (id);


--
-- TOC entry 4860 (class 2606 OID 18804)
-- Name: sensor_data sensor_data_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sensor_data
    ADD CONSTRAINT sensor_data_pkey PRIMARY KEY ("time", device_id, metric_type);


--
-- TOC entry 4888 (class 2606 OID 19016)
-- Name: suggestion_decision_logs suggestion_decision_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggestion_decision_logs
    ADD CONSTRAINT suggestion_decision_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 4881 (class 2606 OID 18993)
-- Name: suggestion_feedback_logs suggestion_feedback_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggestion_feedback_logs
    ADD CONSTRAINT suggestion_feedback_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 4871 (class 2606 OID 18902)
-- Name: suggestion_logs suggestion_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggestion_logs
    ADD CONSTRAINT suggestion_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 4878 (class 2606 OID 18942)
-- Name: home_users uq_home_user; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.home_users
    ADD CONSTRAINT uq_home_user UNIQUE (home_id, user_id);


--
-- TOC entry 4883 (class 2606 OID 18995)
-- Name: suggestion_feedback_logs uq_suggestion_feedback_suggestion_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggestion_feedback_logs
    ADD CONSTRAINT uq_suggestion_feedback_suggestion_id UNIQUE (suggestion_id);


--
-- TOC entry 4868 (class 2606 OID 18874)
-- Name: user_patterns user_patterns_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_patterns
    ADD CONSTRAINT user_patterns_pkey PRIMARY KEY (id);


--
-- TOC entry 4863 (class 2606 OID 18842)
-- Name: user_presence user_presence_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_presence
    ADD CONSTRAINT user_presence_pkey PRIMARY KEY (id);


--
-- TOC entry 4865 (class 2606 OID 18844)
-- Name: user_presence user_presence_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_presence
    ADD CONSTRAINT user_presence_user_id_key UNIQUE (user_id);


--
-- TOC entry 4843 (class 2606 OID 18710)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4851 (class 1259 OID 18954)
-- Name: ix_activity_logs_home_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activity_logs_home_id ON public.activity_logs USING btree (home_id);


--
-- TOC entry 4852 (class 1259 OID 18761)
-- Name: ix_activity_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activity_logs_id ON public.activity_logs USING btree (id);


--
-- TOC entry 4853 (class 1259 OID 18921)
-- Name: ix_activity_logs_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activity_logs_timestamp ON public.activity_logs USING btree ("timestamp");


--
-- TOC entry 4904 (class 1259 OID 19098)
-- Name: ix_auth_sessions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_auth_sessions_user_id ON public.auth_sessions USING btree (user_id);


--
-- TOC entry 4893 (class 1259 OID 19059)
-- Name: ix_device_logs_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_device_logs_timestamp ON public.device_logs USING btree ("timestamp");


--
-- TOC entry 4848 (class 1259 OID 18740)
-- Name: ix_devices_slug; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_devices_slug ON public.devices USING btree (slug);


--
-- TOC entry 4896 (class 1259 OID 19070)
-- Name: ix_energy_logs_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_energy_logs_timestamp ON public.energy_logs USING btree ("timestamp");


--
-- TOC entry 4876 (class 1259 OID 18953)
-- Name: ix_home_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_home_users_id ON public.home_users USING btree (id);


--
-- TOC entry 4905 (class 1259 OID 19113)
-- Name: ix_password_reset_tokens_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_password_reset_tokens_user_id ON public.password_reset_tokens USING btree (user_id);


--
-- TOC entry 4838 (class 1259 OID 18694)
-- Name: ix_rooms_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_rooms_id ON public.rooms USING btree (id);


--
-- TOC entry 4856 (class 1259 OID 18789)
-- Name: ix_schedules_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_schedules_id ON public.schedules USING btree (id);


--
-- TOC entry 4897 (class 1259 OID 19083)
-- Name: ix_security_events_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_security_events_timestamp ON public.security_events USING btree ("timestamp");


--
-- TOC entry 4884 (class 1259 OID 19033)
-- Name: ix_suggestion_decision_logs_home_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suggestion_decision_logs_home_id ON public.suggestion_decision_logs USING btree (home_id);


--
-- TOC entry 4885 (class 1259 OID 19032)
-- Name: ix_suggestion_decision_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suggestion_decision_logs_id ON public.suggestion_decision_logs USING btree (id);


--
-- TOC entry 4886 (class 1259 OID 19034)
-- Name: ix_suggestion_decision_logs_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suggestion_decision_logs_user_id ON public.suggestion_decision_logs USING btree (user_id);


--
-- TOC entry 4879 (class 1259 OID 19006)
-- Name: ix_suggestion_feedback_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suggestion_feedback_logs_id ON public.suggestion_feedback_logs USING btree (id);


--
-- TOC entry 4869 (class 1259 OID 18913)
-- Name: ix_suggestion_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suggestion_logs_id ON public.suggestion_logs USING btree (id);


--
-- TOC entry 4866 (class 1259 OID 18885)
-- Name: ix_user_patterns_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_patterns_id ON public.user_patterns USING btree (id);


--
-- TOC entry 4861 (class 1259 OID 18855)
-- Name: ix_user_presence_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_presence_id ON public.user_presence USING btree (id);


--
-- TOC entry 4841 (class 1259 OID 18711)
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- TOC entry 4916 (class 2606 OID 18751)
-- Name: activity_logs activity_logs_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id);


--
-- TOC entry 4917 (class 2606 OID 18955)
-- Name: activity_logs activity_logs_home_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_home_id_fkey FOREIGN KEY (home_id) REFERENCES public.homes(id);


--
-- TOC entry 4918 (class 2606 OID 18756)
-- Name: activity_logs activity_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 4942 (class 2606 OID 19093)
-- Name: auth_sessions auth_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_sessions
    ADD CONSTRAINT auth_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 4945 (class 2606 OID 19133)
-- Name: automation_actions automation_actions_automation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.automation_actions
    ADD CONSTRAINT automation_actions_automation_id_fkey FOREIGN KEY (automation_id) REFERENCES public.automations(id) ON DELETE CASCADE;


--
-- TOC entry 4946 (class 2606 OID 19138)
-- Name: automation_actions automation_actions_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.automation_actions
    ADD CONSTRAINT automation_actions_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id);


--
-- TOC entry 4944 (class 2606 OID 19121)
-- Name: automation_conditions automation_conditions_automation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.automation_conditions
    ADD CONSTRAINT automation_conditions_automation_id_fkey FOREIGN KEY (automation_id) REFERENCES public.automations(id) ON DELETE CASCADE;


--
-- TOC entry 4938 (class 2606 OID 19042)
-- Name: automations automations_home_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.automations
    ADD CONSTRAINT automations_home_id_fkey FOREIGN KEY (home_id) REFERENCES public.homes(id) ON DELETE CASCADE;


--
-- TOC entry 4939 (class 2606 OID 19054)
-- Name: device_logs device_logs_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.device_logs
    ADD CONSTRAINT device_logs_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id) ON DELETE CASCADE;


--
-- TOC entry 4919 (class 2606 OID 18770)
-- Name: device_states device_states_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.device_states
    ADD CONSTRAINT device_states_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id) ON DELETE CASCADE;


--
-- TOC entry 4915 (class 2606 OID 18735)
-- Name: devices devices_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.rooms(id) ON DELETE SET NULL;


--
-- TOC entry 4940 (class 2606 OID 19065)
-- Name: energy_logs energy_logs_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.energy_logs
    ADD CONSTRAINT energy_logs_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id) ON DELETE CASCADE;


--
-- TOC entry 4931 (class 2606 OID 18943)
-- Name: home_users home_users_home_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.home_users
    ADD CONSTRAINT home_users_home_id_fkey FOREIGN KEY (home_id) REFERENCES public.homes(id) ON DELETE CASCADE;


--
-- TOC entry 4932 (class 2606 OID 18948)
-- Name: home_users home_users_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.home_users
    ADD CONSTRAINT home_users_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 4943 (class 2606 OID 19108)
-- Name: password_reset_tokens password_reset_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 4914 (class 2606 OID 18960)
-- Name: rooms rooms_home_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_home_id_fkey FOREIGN KEY (home_id) REFERENCES public.homes(id) ON DELETE CASCADE;


--
-- TOC entry 4920 (class 2606 OID 18784)
-- Name: schedules schedules_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id) ON DELETE CASCADE;


--
-- TOC entry 4921 (class 2606 OID 18922)
-- Name: schedules schedules_source_suggestion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_source_suggestion_id_fkey FOREIGN KEY (source_suggestion_id) REFERENCES public.suggestion_logs(id);


--
-- TOC entry 4941 (class 2606 OID 19078)
-- Name: security_events security_events_home_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_events
    ADD CONSTRAINT security_events_home_id_fkey FOREIGN KEY (home_id) REFERENCES public.homes(id) ON DELETE CASCADE;


--
-- TOC entry 4922 (class 2606 OID 18805)
-- Name: sensor_data sensor_data_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sensor_data
    ADD CONSTRAINT sensor_data_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id);


--
-- TOC entry 4935 (class 2606 OID 19017)
-- Name: suggestion_decision_logs suggestion_decision_logs_home_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggestion_decision_logs
    ADD CONSTRAINT suggestion_decision_logs_home_id_fkey FOREIGN KEY (home_id) REFERENCES public.homes(id) ON DELETE CASCADE;


--
-- TOC entry 4936 (class 2606 OID 19022)
-- Name: suggestion_decision_logs suggestion_decision_logs_pattern_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggestion_decision_logs
    ADD CONSTRAINT suggestion_decision_logs_pattern_id_fkey FOREIGN KEY (pattern_id) REFERENCES public.user_patterns(id) ON DELETE CASCADE;


--
-- TOC entry 4937 (class 2606 OID 19027)
-- Name: suggestion_decision_logs suggestion_decision_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggestion_decision_logs
    ADD CONSTRAINT suggestion_decision_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 4933 (class 2606 OID 18996)
-- Name: suggestion_feedback_logs suggestion_feedback_logs_suggestion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggestion_feedback_logs
    ADD CONSTRAINT suggestion_feedback_logs_suggestion_id_fkey FOREIGN KEY (suggestion_id) REFERENCES public.suggestion_logs(id) ON DELETE CASCADE;


--
-- TOC entry 4934 (class 2606 OID 19001)
-- Name: suggestion_feedback_logs suggestion_feedback_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggestion_feedback_logs
    ADD CONSTRAINT suggestion_feedback_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 4929 (class 2606 OID 18903)
-- Name: suggestion_logs suggestion_logs_pattern_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggestion_logs
    ADD CONSTRAINT suggestion_logs_pattern_id_fkey FOREIGN KEY (pattern_id) REFERENCES public.user_patterns(id);


--
-- TOC entry 4930 (class 2606 OID 18908)
-- Name: suggestion_logs suggestion_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggestion_logs
    ADD CONSTRAINT suggestion_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 4926 (class 2606 OID 18875)
-- Name: user_patterns user_patterns_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_patterns
    ADD CONSTRAINT user_patterns_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id);


--
-- TOC entry 4927 (class 2606 OID 18965)
-- Name: user_patterns user_patterns_home_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_patterns
    ADD CONSTRAINT user_patterns_home_id_fkey FOREIGN KEY (home_id) REFERENCES public.homes(id);


--
-- TOC entry 4928 (class 2606 OID 18880)
-- Name: user_patterns user_patterns_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_patterns
    ADD CONSTRAINT user_patterns_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 4923 (class 2606 OID 18970)
-- Name: user_presence user_presence_home_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_presence
    ADD CONSTRAINT user_presence_home_id_fkey FOREIGN KEY (home_id) REFERENCES public.homes(id);


--
-- TOC entry 4924 (class 2606 OID 18845)
-- Name: user_presence user_presence_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_presence
    ADD CONSTRAINT user_presence_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.rooms(id);


--
-- TOC entry 4925 (class 2606 OID 18850)
-- Name: user_presence user_presence_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_presence
    ADD CONSTRAINT user_presence_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 5129 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2026-05-28 12:05:58

--
-- PostgreSQL database dump complete
--

\unrestrict xtKwwQXEt1rheh3zD1FzjC8nOK0Xmnf3PsaXUoutCoiJff2bELBHPbrBDdpreUr

