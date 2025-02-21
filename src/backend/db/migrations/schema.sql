

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


CREATE EXTENSION IF NOT EXISTS "pg_cron" WITH SCHEMA "pg_catalog";






CREATE EXTENSION IF NOT EXISTS "pgsodium" WITH SCHEMA "pgsodium";






COMMENT ON SCHEMA "public" IS 'standard public schema';



CREATE EXTENSION IF NOT EXISTS "pg_graphql" WITH SCHEMA "graphql";






CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "pgjwt" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";






CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";






CREATE OR REPLACE FUNCTION "public"."delete_old_checkpoints"() RETURNS "void"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    -- Delete from checkpoints table
    DELETE FROM public.checkpoints
    WHERE thread_id IN (
        SELECT c.thread_id 
        FROM public.checkpoints c
        LEFT JOIN public.content ct ON c.thread_id = ct.thread_id::text
        WHERE ct.status = 'Published'
        AND ct.created_at < NOW() - INTERVAL '10 days'
    );

    -- Delete from checkpoint_writes
    DELETE FROM public.checkpoint_writes
    WHERE thread_id IN (
        SELECT cw.thread_id 
        FROM public.checkpoint_writes cw
        LEFT JOIN public.content ct ON cw.thread_id = ct.thread_id::text
        WHERE ct.status = 'Published'
        AND ct.created_at < NOW() - INTERVAL '10 days'
    );

    -- Delete from checkpoint_blobs
    DELETE FROM public.checkpoint_blobs
    WHERE thread_id IN (
        SELECT cb.thread_id 
        FROM public.checkpoint_blobs cb
        LEFT JOIN public.content ct ON cb.thread_id = ct.thread_id::text
        WHERE ct.status = 'Published'
        AND ct.created_at < NOW() - INTERVAL '10 days'
    );
END;
$$;


ALTER FUNCTION "public"."delete_old_checkpoints"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."filter_content_by_domain"("domain_text" "text") RETURNS TABLE("content_id" "uuid", "title" "text", "body" "text", "status" "text", "created_at" timestamp with time zone, "updated_at" timestamp with time zone, "published_at" timestamp with time zone, "thread_id" "uuid", "content_type_id" "uuid", "content_type_name" "text", "tag_id" "uuid", "tag_name" "text", "content_source_id" "uuid", "source_id" "uuid", "source_identifier" "text", "source_type_name" "text", "url_references" "jsonb", "media" "jsonb")
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.content_id,
        c.title,
        c.body,
        c.status,
        c.created_at,
        c.updated_at,
        c.published_at,
        c.thread_id,
        ct.content_type_id,
        ct.name AS content_type_name,
        t.tag_id,
        t.name AS tag_name,
        cs.content_source_id,
        s.source_id,
        s.source_identifier,
        st.name AS source_type_name,
        s.url_references,
        s.media
    FROM
        content c
        LEFT JOIN content_types ct ON c.content_type_id = ct.content_type_id
        LEFT JOIN content_tags ctg ON c.content_id = ctg.content_id
        LEFT JOIN tags t ON ctg.tag_id = t.tag_id
        LEFT JOIN content_sources cs ON c.content_id = cs.content_id
        LEFT JOIN sources s ON cs.source_id = s.source_id
        LEFT JOIN source_types st ON s.source_type_id = st.source_type_id
    WHERE
        s.url_references @> jsonb_build_object('domain', domain_text);
END;
$$;


ALTER FUNCTION "public"."filter_content_by_domain"("domain_text" "text") OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."handle_new_user"() RETURNS "trigger"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
BEGIN
  INSERT INTO public.profiles (id, user_id, role, subscription_status, created_at)
  VALUES (
    gen_random_uuid(),  -- Generate a new UUID for the id
    NEW.id,
    'free',
    'none',
    NOW()
  )
  ON CONFLICT (user_id) DO NOTHING;
  RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."handle_new_user"() OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."checkpoint_blobs" (
    "thread_id" "text" NOT NULL,
    "checkpoint_ns" "text" DEFAULT ''::"text" NOT NULL,
    "channel" "text" NOT NULL,
    "version" "text" NOT NULL,
    "type" "text" NOT NULL,
    "blob" "bytea"
);


ALTER TABLE "public"."checkpoint_blobs" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."checkpoint_migrations" (
    "v" integer NOT NULL
);


ALTER TABLE "public"."checkpoint_migrations" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."checkpoint_writes" (
    "thread_id" "text" NOT NULL,
    "checkpoint_ns" "text" DEFAULT ''::"text" NOT NULL,
    "checkpoint_id" "text" NOT NULL,
    "task_id" "text" NOT NULL,
    "idx" integer NOT NULL,
    "channel" "text" NOT NULL,
    "type" "text",
    "blob" "bytea" NOT NULL,
    "task_path" "text" DEFAULT ''::"text" NOT NULL
);


ALTER TABLE "public"."checkpoint_writes" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."checkpoints" (
    "thread_id" "text" NOT NULL,
    "checkpoint_ns" "text" DEFAULT ''::"text" NOT NULL,
    "checkpoint_id" "text" NOT NULL,
    "parent_checkpoint_id" "text",
    "type" "text",
    "checkpoint" "jsonb" NOT NULL,
    "metadata" "jsonb" DEFAULT '{}'::"jsonb" NOT NULL
);


ALTER TABLE "public"."checkpoints" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."content" (
    "content_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "profile_id" "uuid" NOT NULL,
    "content_type_id" "uuid",
    "title" "text",
    "body" "text",
    "status" "text" DEFAULT '''Draft''::text'::"text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "published_at" timestamp with time zone,
    "thread_id" "uuid",
    "is_deleted" boolean DEFAULT false,
    "deleted_at" timestamp with time zone,
    "template_id" "uuid",
    CONSTRAINT "status_check" CHECK (("status" = ANY (ARRAY['Draft'::"text", 'Published'::"text", 'Archived'::"text", 'Scheduled'::"text", 'Rejected'::"text"])))
);


ALTER TABLE "public"."content" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."content_analytics" (
    "analytics_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "content_id" "uuid",
    "views" integer DEFAULT 0,
    "likes" integer DEFAULT 0,
    "shares" integer DEFAULT 0,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."content_analytics" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."content_sources" (
    "content_source_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "content_id" "uuid",
    "source_id" "uuid",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "is_deleted" boolean DEFAULT false,
    "deleted_at" timestamp with time zone
);


ALTER TABLE "public"."content_sources" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."content_tags" (
    "content_tag_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "content_id" "uuid",
    "tag_id" "uuid",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "is_deleted" boolean DEFAULT false,
    "deleted_at" timestamp with time zone
);


ALTER TABLE "public"."content_tags" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."content_types" (
    "content_type_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "name" "text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."content_types" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."custom_field_values" (
    "custom_field_value_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "source_id" "uuid",
    "custom_field_id" "uuid",
    "value" "text",
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."custom_field_values" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."custom_fields" (
    "custom_field_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "source_type" "text" NOT NULL,
    "field_name" "text" NOT NULL,
    "field_type" "text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "custom_fields_field_type_check" CHECK (("field_type" = ANY (ARRAY['string'::"text", 'number'::"text", 'boolean'::"text", 'date'::"text"]))),
    CONSTRAINT "custom_fields_source_type_check" CHECK (("source_type" = ANY (ARRAY['twitter'::"text", 'web_url'::"text", 'linkedin'::"text", 'github'::"text"])))
);


ALTER TABLE "public"."custom_fields" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."generation_limits" (
    "tier" "text" NOT NULL,
    "max_generations" integer NOT NULL
);


ALTER TABLE "public"."generation_limits" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."media" (
    "media_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "source_id" "uuid",
    "media_url" "text" NOT NULL,
    "media_type" "text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "is_deleted" boolean DEFAULT false,
    "deleted_at" timestamp with time zone
);


ALTER TABLE "public"."media" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."parameter_values" (
    "value_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "parameter_id" "uuid",
    "value" "text" NOT NULL,
    "display_order" integer,
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."parameter_values" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."parameters" (
    "parameter_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "name" "text" NOT NULL,
    "display_name" "text" NOT NULL,
    "description" "text",
    "is_required" boolean DEFAULT false,
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."parameters" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."payments" (
    "payment_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "subscription_id" "uuid",
    "amount" numeric(10,2) NOT NULL,
    "payment_method" "text" NOT NULL,
    "status" "text" DEFAULT 'pending'::"text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "payments_payment_method_check" CHECK (("payment_method" = ANY (ARRAY['credit_card'::"text", 'paypal'::"text", 'stripe'::"text"]))),
    CONSTRAINT "payments_status_check" CHECK (("status" = ANY (ARRAY['success'::"text", 'failed'::"text", 'pending'::"text"])))
);


ALTER TABLE "public"."payments" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."plans" (
    "plan_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "name" "text" NOT NULL,
    "price" numeric(10,2) NOT NULL,
    "features" "jsonb",
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."plans" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."profiles" (
    "id" "uuid" NOT NULL,
    "user_id" "uuid" NOT NULL,
    "full_name" "text",
    "avatar_url" "text",
    "role" "text" DEFAULT 'free'::"text",
    "subscription_status" "text" DEFAULT 'none'::"text",
    "subscription_end" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "preferences" "jsonb" DEFAULT '{"theme": "light", "defaultView": "blog", "emailNotifications": true}'::"jsonb",
    "is_deleted" boolean DEFAULT false,
    "deleted_at" timestamp with time zone,
    "generations_used" integer DEFAULT 0,
    "bio" "text",
    "website" "text",
    "company" "text",
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "email" "text",
    CONSTRAINT "profiles_role_check" CHECK (("role" = ANY (ARRAY['free'::"text", 'basic'::"text", 'premium'::"text"]))),
    CONSTRAINT "profiles_subscription_status_check" CHECK (("subscription_status" = ANY (ARRAY['active'::"text", 'trialing'::"text", 'cancelled'::"text", 'none'::"text"])))
);


ALTER TABLE "public"."profiles" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."quota_usage" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "profile_id" "uuid",
    "quota_type" "text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."quota_usage" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."rate_limits" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "profile_id" "uuid",
    "action_type" "text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."rate_limits" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."source_metadata" (
    "metadata_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "source_id" "uuid",
    "key" "text" NOT NULL,
    "value" "text",
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."source_metadata" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."source_types" (
    "source_type_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "name" "text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."source_types" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."sources" (
    "source_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "source_identifier" "text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "batch_id" "uuid",
    "source_type_id" "uuid" NOT NULL,
    "profile_id" "uuid" NOT NULL,
    "is_deleted" boolean DEFAULT false,
    "deleted_at" timestamp with time zone
);


ALTER TABLE "public"."sources" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."subscriptions" (
    "subscription_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "profile_id" "uuid",
    "plan_id" "uuid",
    "start_date" timestamp with time zone NOT NULL,
    "end_date" timestamp with time zone,
    "status" "text" DEFAULT 'active'::"text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "subscriptions_status_check" CHECK (("status" = ANY (ARRAY['active'::"text", 'canceled'::"text", 'expired'::"text"])))
);


ALTER TABLE "public"."subscriptions" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."tags" (
    "tag_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "name" "text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "is_deleted" boolean DEFAULT false,
    "deleted_at" timestamp with time zone
);


ALTER TABLE "public"."tags" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."template_parameters" (
    "template_param_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "template_id" "uuid",
    "parameter_id" "uuid",
    "value_id" "uuid",
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."template_parameters" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."templates" (
    "template_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "name" "text" NOT NULL,
    "description" "text",
    "template_type" "text" DEFAULT 'default'::"text",
    "profile_id" "uuid",
    "template_image_url" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "is_deleted" boolean DEFAULT false,
    CONSTRAINT "templates_template_type_check" CHECK (("template_type" = ANY (ARRAY['default'::"text", 'custom'::"text"])))
);


ALTER TABLE "public"."templates" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."url_references" (
    "url_reference_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "source_id" "uuid",
    "url" "text" NOT NULL,
    "description" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "type" "text",
    "domain" "text",
    "content_type" "text",
    "file_category" "text",
    "is_deleted" boolean DEFAULT false,
    "deleted_at" timestamp with time zone
);


ALTER TABLE "public"."url_references" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."user_activity" (
    "activity_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "profile_id" "uuid",
    "activity_type" "text" NOT NULL,
    "activity_details" "jsonb",
    "created_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "user_activity_activity_type_check" CHECK (("activity_type" = ANY (ARRAY['login'::"text", 'blog_created'::"text", 'blog_published'::"text"])))
);


ALTER TABLE "public"."user_activity" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."user_generations" (
    "user_thread_generation_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "profile_id" "uuid",
    "generations_used" integer DEFAULT 0,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."user_generations" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."user_selected_sources" (
    "selection_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "profile_id" "uuid",
    "source_id" "uuid",
    "selected_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."user_selected_sources" OWNER TO "postgres";


ALTER TABLE ONLY "public"."checkpoint_blobs"
    ADD CONSTRAINT "checkpoint_blobs_pkey" PRIMARY KEY ("thread_id", "checkpoint_ns", "channel", "version");



ALTER TABLE ONLY "public"."checkpoint_migrations"
    ADD CONSTRAINT "checkpoint_migrations_pkey" PRIMARY KEY ("v");



ALTER TABLE ONLY "public"."checkpoint_writes"
    ADD CONSTRAINT "checkpoint_writes_pkey" PRIMARY KEY ("thread_id", "checkpoint_ns", "checkpoint_id", "task_id", "idx");



ALTER TABLE ONLY "public"."checkpoints"
    ADD CONSTRAINT "checkpoints_pkey" PRIMARY KEY ("thread_id", "checkpoint_ns", "checkpoint_id");



ALTER TABLE ONLY "public"."content_analytics"
    ADD CONSTRAINT "content_analytics_pkey" PRIMARY KEY ("analytics_id");



ALTER TABLE ONLY "public"."content"
    ADD CONSTRAINT "content_pkey" PRIMARY KEY ("content_id");



ALTER TABLE ONLY "public"."content_sources"
    ADD CONSTRAINT "content_sources_pkey" PRIMARY KEY ("content_source_id");



ALTER TABLE ONLY "public"."content_tags"
    ADD CONSTRAINT "content_tags_pkey" PRIMARY KEY ("content_tag_id");



ALTER TABLE ONLY "public"."content_types"
    ADD CONSTRAINT "content_types_name_key" UNIQUE ("name");



ALTER TABLE ONLY "public"."content_types"
    ADD CONSTRAINT "content_types_pkey" PRIMARY KEY ("content_type_id");



ALTER TABLE ONLY "public"."custom_field_values"
    ADD CONSTRAINT "custom_field_values_pkey" PRIMARY KEY ("custom_field_value_id");



ALTER TABLE ONLY "public"."custom_fields"
    ADD CONSTRAINT "custom_fields_pkey" PRIMARY KEY ("custom_field_id");



ALTER TABLE ONLY "public"."generation_limits"
    ADD CONSTRAINT "generation_limits_pkey" PRIMARY KEY ("tier");



ALTER TABLE ONLY "public"."media"
    ADD CONSTRAINT "media_pkey" PRIMARY KEY ("media_id");



ALTER TABLE ONLY "public"."source_metadata"
    ADD CONSTRAINT "metadata_pkey" PRIMARY KEY ("metadata_id");



ALTER TABLE ONLY "public"."parameter_values"
    ADD CONSTRAINT "parameter_values_parameter_id_value_key" UNIQUE ("parameter_id", "value");



ALTER TABLE ONLY "public"."parameter_values"
    ADD CONSTRAINT "parameter_values_pkey" PRIMARY KEY ("value_id");



ALTER TABLE ONLY "public"."parameters"
    ADD CONSTRAINT "parameters_name_key" UNIQUE ("name");



ALTER TABLE ONLY "public"."parameters"
    ADD CONSTRAINT "parameters_pkey" PRIMARY KEY ("parameter_id");



ALTER TABLE ONLY "public"."payments"
    ADD CONSTRAINT "payments_pkey" PRIMARY KEY ("payment_id");



ALTER TABLE ONLY "public"."plans"
    ADD CONSTRAINT "plans_pkey" PRIMARY KEY ("plan_id");



ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "profiles_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."quota_usage"
    ADD CONSTRAINT "quota_usage_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."rate_limits"
    ADD CONSTRAINT "rate_limits_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."source_types"
    ADD CONSTRAINT "source_types_name_key" UNIQUE ("name");



ALTER TABLE ONLY "public"."source_types"
    ADD CONSTRAINT "source_types_pkey" PRIMARY KEY ("source_type_id");



ALTER TABLE ONLY "public"."sources"
    ADD CONSTRAINT "sources_pkey" PRIMARY KEY ("source_id");



ALTER TABLE ONLY "public"."subscriptions"
    ADD CONSTRAINT "subscriptions_pkey" PRIMARY KEY ("subscription_id");



ALTER TABLE ONLY "public"."tags"
    ADD CONSTRAINT "tags_name_key" UNIQUE ("name");



ALTER TABLE ONLY "public"."tags"
    ADD CONSTRAINT "tags_pkey" PRIMARY KEY ("tag_id");



ALTER TABLE ONLY "public"."template_parameters"
    ADD CONSTRAINT "template_parameters_pkey" PRIMARY KEY ("template_param_id");



ALTER TABLE ONLY "public"."template_parameters"
    ADD CONSTRAINT "template_parameters_template_id_parameter_id_key" UNIQUE ("template_id", "parameter_id");



ALTER TABLE ONLY "public"."templates"
    ADD CONSTRAINT "templates_pkey" PRIMARY KEY ("template_id");



ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "unique_user_profile" UNIQUE ("user_id");



ALTER TABLE ONLY "public"."url_references"
    ADD CONSTRAINT "url_references_pkey" PRIMARY KEY ("url_reference_id");



ALTER TABLE ONLY "public"."user_activity"
    ADD CONSTRAINT "user_activity_pkey" PRIMARY KEY ("activity_id");



ALTER TABLE ONLY "public"."user_selected_sources"
    ADD CONSTRAINT "user_selected_sources_pkey" PRIMARY KEY ("selection_id");



ALTER TABLE ONLY "public"."user_generations"
    ADD CONSTRAINT "user_thread_generations_pkey" PRIMARY KEY ("user_thread_generation_id");



CREATE INDEX "checkpoint_blobs_thread_id_idx" ON "public"."checkpoint_blobs" USING "btree" ("thread_id");



CREATE INDEX "checkpoint_writes_thread_id_idx" ON "public"."checkpoint_writes" USING "btree" ("thread_id");



CREATE INDEX "checkpoints_thread_id_idx" ON "public"."checkpoints" USING "btree" ("thread_id");



CREATE INDEX "idx_content_is_deleted" ON "public"."content" USING "btree" ("is_deleted");



CREATE INDEX "idx_media_is_deleted" ON "public"."media" USING "btree" ("is_deleted");



CREATE INDEX "idx_profiles_is_deleted" ON "public"."profiles" USING "btree" ("is_deleted");



CREATE INDEX "idx_sources_is_deleted" ON "public"."sources" USING "btree" ("is_deleted");



CREATE INDEX "idx_sources_profile_id" ON "public"."sources" USING "btree" ("profile_id");



CREATE INDEX "idx_url_references_is_deleted" ON "public"."url_references" USING "btree" ("is_deleted");



CREATE INDEX "idx_user_thread_generations_profile_id" ON "public"."user_generations" USING "btree" ("profile_id");



ALTER TABLE ONLY "public"."content_analytics"
    ADD CONSTRAINT "content_analytics_content_id_fkey" FOREIGN KEY ("content_id") REFERENCES "public"."content"("content_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."content"
    ADD CONSTRAINT "content_content_type_id_fkey" FOREIGN KEY ("content_type_id") REFERENCES "public"."content_types"("content_type_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."content"
    ADD CONSTRAINT "content_profile_id_fkey" FOREIGN KEY ("profile_id") REFERENCES "public"."profiles"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."content_sources"
    ADD CONSTRAINT "content_sources_content_id_fkey" FOREIGN KEY ("content_id") REFERENCES "public"."content"("content_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."content_sources"
    ADD CONSTRAINT "content_sources_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "public"."sources"("source_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."content_tags"
    ADD CONSTRAINT "content_tags_content_id_fkey" FOREIGN KEY ("content_id") REFERENCES "public"."content"("content_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."content_tags"
    ADD CONSTRAINT "content_tags_tag_id_fkey" FOREIGN KEY ("tag_id") REFERENCES "public"."tags"("tag_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."content"
    ADD CONSTRAINT "content_template_id_fkey" FOREIGN KEY ("template_id") REFERENCES "public"."templates"("template_id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."custom_field_values"
    ADD CONSTRAINT "custom_field_values_custom_field_id_fkey" FOREIGN KEY ("custom_field_id") REFERENCES "public"."custom_fields"("custom_field_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."custom_field_values"
    ADD CONSTRAINT "custom_field_values_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "public"."sources"("source_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "fk_profiles_users" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."sources"
    ADD CONSTRAINT "fk_source_type" FOREIGN KEY ("source_type_id") REFERENCES "public"."source_types"("source_type_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."media"
    ADD CONSTRAINT "media_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "public"."sources"("source_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."source_metadata"
    ADD CONSTRAINT "metadata_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "public"."sources"("source_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."parameter_values"
    ADD CONSTRAINT "parameter_values_parameter_id_fkey" FOREIGN KEY ("parameter_id") REFERENCES "public"."parameters"("parameter_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."payments"
    ADD CONSTRAINT "payments_subscription_id_fkey" FOREIGN KEY ("subscription_id") REFERENCES "public"."subscriptions"("subscription_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "profiles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."quota_usage"
    ADD CONSTRAINT "quota_usage_profile_id_fkey" FOREIGN KEY ("profile_id") REFERENCES "public"."profiles"("id");



ALTER TABLE ONLY "public"."rate_limits"
    ADD CONSTRAINT "rate_limits_profile_id_fkey" FOREIGN KEY ("profile_id") REFERENCES "public"."profiles"("id");



ALTER TABLE ONLY "public"."sources"
    ADD CONSTRAINT "sources_profile_id_fkey" FOREIGN KEY ("profile_id") REFERENCES "public"."profiles"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."subscriptions"
    ADD CONSTRAINT "subscriptions_plan_id_fkey" FOREIGN KEY ("plan_id") REFERENCES "public"."plans"("plan_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."subscriptions"
    ADD CONSTRAINT "subscriptions_profile_id_fkey" FOREIGN KEY ("profile_id") REFERENCES "public"."profiles"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."template_parameters"
    ADD CONSTRAINT "template_parameters_parameter_id_fkey" FOREIGN KEY ("parameter_id") REFERENCES "public"."parameters"("parameter_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."template_parameters"
    ADD CONSTRAINT "template_parameters_template_id_fkey" FOREIGN KEY ("template_id") REFERENCES "public"."templates"("template_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."template_parameters"
    ADD CONSTRAINT "template_parameters_value_id_fkey" FOREIGN KEY ("value_id") REFERENCES "public"."parameter_values"("value_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."templates"
    ADD CONSTRAINT "templates_profile_id_fkey" FOREIGN KEY ("profile_id") REFERENCES "public"."profiles"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."url_references"
    ADD CONSTRAINT "url_references_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "public"."sources"("source_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."user_activity"
    ADD CONSTRAINT "user_activity_profile_id_fkey" FOREIGN KEY ("profile_id") REFERENCES "public"."profiles"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."user_selected_sources"
    ADD CONSTRAINT "user_selected_sources_profile_id_fkey" FOREIGN KEY ("profile_id") REFERENCES "public"."profiles"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."user_selected_sources"
    ADD CONSTRAINT "user_selected_sources_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "public"."sources"("source_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."user_generations"
    ADD CONSTRAINT "user_thread_generations_profile_id_fkey" FOREIGN KEY ("profile_id") REFERENCES "public"."profiles"("id") ON DELETE CASCADE;



CREATE POLICY "Allow initial profile creation" ON "public"."profiles" FOR INSERT WITH CHECK (true);



CREATE POLICY "Public profiles are viewable by everyone." ON "public"."profiles" FOR SELECT USING (true);



CREATE POLICY "Users can delete own profile" ON "public"."profiles" FOR DELETE USING ((("auth"."uid"() = "user_id") OR ("auth"."role"() = 'service_role'::"text")));



CREATE POLICY "Users can insert their own profile." ON "public"."profiles" FOR INSERT WITH CHECK (("auth"."uid"() = "user_id"));



CREATE POLICY "Users can update own profile" ON "public"."profiles" FOR UPDATE USING ((("auth"."uid"() = "user_id") OR ("auth"."role"() = 'service_role'::"text")));



CREATE POLICY "Users can update own profile." ON "public"."profiles" FOR UPDATE USING (("auth"."uid"() = "user_id"));



CREATE POLICY "Users can view own profile" ON "public"."profiles" FOR SELECT USING ((("auth"."uid"() = "user_id") OR ("auth"."role"() = 'service_role'::"text")));



ALTER TABLE "public"."profiles" ENABLE ROW LEVEL SECURITY;




ALTER PUBLICATION "supabase_realtime" OWNER TO "postgres";





GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";









































































































































































































GRANT ALL ON FUNCTION "public"."delete_old_checkpoints"() TO "anon";
GRANT ALL ON FUNCTION "public"."delete_old_checkpoints"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."delete_old_checkpoints"() TO "service_role";



GRANT ALL ON FUNCTION "public"."filter_content_by_domain"("domain_text" "text") TO "anon";
GRANT ALL ON FUNCTION "public"."filter_content_by_domain"("domain_text" "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."filter_content_by_domain"("domain_text" "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."handle_new_user"() TO "anon";
GRANT ALL ON FUNCTION "public"."handle_new_user"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."handle_new_user"() TO "service_role";
























GRANT ALL ON TABLE "public"."checkpoint_blobs" TO "anon";
GRANT ALL ON TABLE "public"."checkpoint_blobs" TO "authenticated";
GRANT ALL ON TABLE "public"."checkpoint_blobs" TO "service_role";



GRANT ALL ON TABLE "public"."checkpoint_migrations" TO "anon";
GRANT ALL ON TABLE "public"."checkpoint_migrations" TO "authenticated";
GRANT ALL ON TABLE "public"."checkpoint_migrations" TO "service_role";



GRANT ALL ON TABLE "public"."checkpoint_writes" TO "anon";
GRANT ALL ON TABLE "public"."checkpoint_writes" TO "authenticated";
GRANT ALL ON TABLE "public"."checkpoint_writes" TO "service_role";



GRANT ALL ON TABLE "public"."checkpoints" TO "anon";
GRANT ALL ON TABLE "public"."checkpoints" TO "authenticated";
GRANT ALL ON TABLE "public"."checkpoints" TO "service_role";



GRANT ALL ON TABLE "public"."content" TO "anon";
GRANT ALL ON TABLE "public"."content" TO "authenticated";
GRANT ALL ON TABLE "public"."content" TO "service_role";



GRANT ALL ON TABLE "public"."content_analytics" TO "anon";
GRANT ALL ON TABLE "public"."content_analytics" TO "authenticated";
GRANT ALL ON TABLE "public"."content_analytics" TO "service_role";



GRANT ALL ON TABLE "public"."content_sources" TO "anon";
GRANT ALL ON TABLE "public"."content_sources" TO "authenticated";
GRANT ALL ON TABLE "public"."content_sources" TO "service_role";



GRANT ALL ON TABLE "public"."content_tags" TO "anon";
GRANT ALL ON TABLE "public"."content_tags" TO "authenticated";
GRANT ALL ON TABLE "public"."content_tags" TO "service_role";



GRANT ALL ON TABLE "public"."content_types" TO "anon";
GRANT ALL ON TABLE "public"."content_types" TO "authenticated";
GRANT ALL ON TABLE "public"."content_types" TO "service_role";



GRANT ALL ON TABLE "public"."custom_field_values" TO "anon";
GRANT ALL ON TABLE "public"."custom_field_values" TO "authenticated";
GRANT ALL ON TABLE "public"."custom_field_values" TO "service_role";



GRANT ALL ON TABLE "public"."custom_fields" TO "anon";
GRANT ALL ON TABLE "public"."custom_fields" TO "authenticated";
GRANT ALL ON TABLE "public"."custom_fields" TO "service_role";



GRANT ALL ON TABLE "public"."generation_limits" TO "anon";
GRANT ALL ON TABLE "public"."generation_limits" TO "authenticated";
GRANT ALL ON TABLE "public"."generation_limits" TO "service_role";



GRANT ALL ON TABLE "public"."media" TO "anon";
GRANT ALL ON TABLE "public"."media" TO "authenticated";
GRANT ALL ON TABLE "public"."media" TO "service_role";



GRANT ALL ON TABLE "public"."parameter_values" TO "anon";
GRANT ALL ON TABLE "public"."parameter_values" TO "authenticated";
GRANT ALL ON TABLE "public"."parameter_values" TO "service_role";



GRANT ALL ON TABLE "public"."parameters" TO "anon";
GRANT ALL ON TABLE "public"."parameters" TO "authenticated";
GRANT ALL ON TABLE "public"."parameters" TO "service_role";



GRANT ALL ON TABLE "public"."payments" TO "anon";
GRANT ALL ON TABLE "public"."payments" TO "authenticated";
GRANT ALL ON TABLE "public"."payments" TO "service_role";



GRANT ALL ON TABLE "public"."plans" TO "anon";
GRANT ALL ON TABLE "public"."plans" TO "authenticated";
GRANT ALL ON TABLE "public"."plans" TO "service_role";



GRANT ALL ON TABLE "public"."profiles" TO "anon";
GRANT ALL ON TABLE "public"."profiles" TO "authenticated";
GRANT ALL ON TABLE "public"."profiles" TO "service_role";



GRANT ALL ON TABLE "public"."quota_usage" TO "anon";
GRANT ALL ON TABLE "public"."quota_usage" TO "authenticated";
GRANT ALL ON TABLE "public"."quota_usage" TO "service_role";



GRANT ALL ON TABLE "public"."rate_limits" TO "anon";
GRANT ALL ON TABLE "public"."rate_limits" TO "authenticated";
GRANT ALL ON TABLE "public"."rate_limits" TO "service_role";



GRANT ALL ON TABLE "public"."source_metadata" TO "anon";
GRANT ALL ON TABLE "public"."source_metadata" TO "authenticated";
GRANT ALL ON TABLE "public"."source_metadata" TO "service_role";



GRANT ALL ON TABLE "public"."source_types" TO "anon";
GRANT ALL ON TABLE "public"."source_types" TO "authenticated";
GRANT ALL ON TABLE "public"."source_types" TO "service_role";



GRANT ALL ON TABLE "public"."sources" TO "anon";
GRANT ALL ON TABLE "public"."sources" TO "authenticated";
GRANT ALL ON TABLE "public"."sources" TO "service_role";



GRANT ALL ON TABLE "public"."subscriptions" TO "anon";
GRANT ALL ON TABLE "public"."subscriptions" TO "authenticated";
GRANT ALL ON TABLE "public"."subscriptions" TO "service_role";



GRANT ALL ON TABLE "public"."tags" TO "anon";
GRANT ALL ON TABLE "public"."tags" TO "authenticated";
GRANT ALL ON TABLE "public"."tags" TO "service_role";



GRANT ALL ON TABLE "public"."template_parameters" TO "anon";
GRANT ALL ON TABLE "public"."template_parameters" TO "authenticated";
GRANT ALL ON TABLE "public"."template_parameters" TO "service_role";



GRANT ALL ON TABLE "public"."templates" TO "anon";
GRANT ALL ON TABLE "public"."templates" TO "authenticated";
GRANT ALL ON TABLE "public"."templates" TO "service_role";



GRANT ALL ON TABLE "public"."url_references" TO "anon";
GRANT ALL ON TABLE "public"."url_references" TO "authenticated";
GRANT ALL ON TABLE "public"."url_references" TO "service_role";



GRANT ALL ON TABLE "public"."user_activity" TO "anon";
GRANT ALL ON TABLE "public"."user_activity" TO "authenticated";
GRANT ALL ON TABLE "public"."user_activity" TO "service_role";



GRANT ALL ON TABLE "public"."user_generations" TO "anon";
GRANT ALL ON TABLE "public"."user_generations" TO "authenticated";
GRANT ALL ON TABLE "public"."user_generations" TO "service_role";



GRANT ALL ON TABLE "public"."user_selected_sources" TO "anon";
GRANT ALL ON TABLE "public"."user_selected_sources" TO "authenticated";
GRANT ALL ON TABLE "public"."user_selected_sources" TO "service_role";



ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "service_role";






























RESET ALL;
