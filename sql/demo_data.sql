-- Demo Data Script
-- Description: Creates realistic demo companies, users, and projects across global regions
-- Regions: Africa, Latin America, Asia, Europe
-- Date: 2025-12-25
-- Note: This script is safe to run multiple times (uses INSERT ... ON CONFLICT)

-- ============================================================================
-- AFRICA REGION
-- ============================================================================

DO $$
DECLARE
    -- Company IDs
    v_kenya_wildlife_id INTEGER;
    v_tanzania_conservation_id INTEGER;
    v_south_africa_eco_id INTEGER;

    -- User IDs
    v_user_id INTEGER;

    -- Project IDs
    v_project_id INTEGER;
BEGIN
    RAISE NOTICE '==================================================';
    RAISE NOTICE 'Creating Africa Region Demo Data';
    RAISE NOTICE '==================================================';

    -- ========================================
    -- KENYA WILDLIFE TRUST
    -- ========================================
    INSERT INTO companies (company_name, company_code, contact_email, is_active)
    VALUES (
        'Kenya Wildlife Trust',
        'KWT',
        'info@kenyawildlife.org',
        TRUE
    )
    ON CONFLICT (company_code) DO UPDATE SET company_name = EXCLUDED.company_name
    RETURNING id INTO v_kenya_wildlife_id;

    -- Kenya Users
    INSERT INTO users (company_id, username, email, password_hash, full_name, role, is_active)
    VALUES
        (v_kenya_wildlife_id, 'jkamau', 'j.kamau@kenyawildlife.org', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'James Kamau', 'admin', TRUE),
        (v_kenya_wildlife_id, 'aodhiambo', 'a.odhiambo@kenyawildlife.org', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Alice Odhiambo', 'user', TRUE)
    ON CONFLICT (username) DO NOTHING;

    -- Kenya Projects
    INSERT INTO projects (company_id, project_name, bucket_name, aws_region, description, is_active)
    VALUES (
        v_kenya_wildlife_id,
        'Maasai Mara Elephant Monitoring',
        'kwt-maasai-mara-elephants',
        'eu-west-1',
        'Long-term acoustic and camera trap monitoring of elephant populations in Maasai Mara National Reserve',
        TRUE
    )
    ON CONFLICT (project_name) DO NOTHING
    RETURNING id INTO v_project_id;

    IF v_project_id IS NOT NULL THEN
        INSERT INTO cycles (project_id, cycle_name, cycle_number, s3_prefix, status, description)
        VALUES
            (v_project_id, 'C1', 1, 'C1', 'completed', 'January-March 2024 - Dry season baseline'),
            (v_project_id, 'C2', 2, 'C2', 'completed', 'April-June 2024 - Long rains migration'),
            (v_project_id, 'C3', 3, 'C3', 'in_progress', 'July-September 2024 - Post-migration monitoring'),
            (v_project_id, 'C4', 4, 'C4', 'pending', 'October-December 2024 - Short rains season');
    END IF;

    INSERT INTO projects (company_id, project_name, bucket_name, aws_region, description, is_active)
    VALUES (
        v_kenya_wildlife_id,
        'Amboseli Rhino Conservation',
        'kwt-amboseli-rhino',
        'eu-west-1',
        'Camera trap network monitoring black rhinoceros in Amboseli ecosystem',
        TRUE
    )
    ON CONFLICT (project_name) DO NOTHING
    RETURNING id INTO v_project_id;

    IF v_project_id IS NOT NULL THEN
        INSERT INTO cycles (project_id, cycle_name, cycle_number, s3_prefix, status, description)
        VALUES
            (v_project_id, 'C1', 1, 'C1', 'completed', 'Q1 2024 - Initial deployment'),
            (v_project_id, 'C2', 2, 'C2', 'in_progress', 'Q2 2024 - Mid-year collection');
    END IF;

    -- ========================================
    -- TANZANIA CONSERVATION NETWORK
    -- ========================================
    INSERT INTO companies (company_name, company_code, contact_email, is_active)
    VALUES (
        'Tanzania Conservation Network',
        'TCN',
        'contact@tanzaniaconservation.org',
        TRUE
    )
    ON CONFLICT (company_code) DO UPDATE SET company_name = EXCLUDED.company_name
    RETURNING id INTO v_tanzania_conservation_id;

    -- Tanzania Users
    INSERT INTO users (company_id, username, email, password_hash, full_name, role, is_active)
    VALUES
        (v_tanzania_conservation_id, 'hmwinyi', 'h.mwinyi@tanzaniaconservation.org', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Hassan Mwinyi', 'admin', TRUE),
        (v_tanzania_conservation_id, 'pngonyani', 'p.ngonyani@tanzaniaconservation.org', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Prisca Ngonyani', 'user', TRUE),
        (v_tanzania_conservation_id, 'dkiondo', 'd.kiondo@tanzaniaconservation.org', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Daniel Kiondo', 'user', TRUE)
    ON CONFLICT (username) DO NOTHING;

    -- Tanzania Projects
    INSERT INTO projects (company_id, project_name, bucket_name, aws_region, description, is_active)
    VALUES (
        v_tanzania_conservation_id,
        'Serengeti Wildebeest Migration',
        'tcn-serengeti-migration',
        'eu-west-1',
        'Ultrasonic and audible acoustic monitoring of the great wildebeest migration',
        TRUE
    )
    ON CONFLICT (project_name) DO NOTHING
    RETURNING id INTO v_project_id;

    IF v_project_id IS NOT NULL THEN
        INSERT INTO cycles (project_id, cycle_name, cycle_number, s3_prefix, status, description)
        VALUES
            (v_project_id, 'C1', 1, 'C1', 'completed', 'December-February - Southern plains'),
            (v_project_id, 'C2', 2, 'C2', 'completed', 'March-May - Western corridor'),
            (v_project_id, 'C3', 3, 'C3', 'completed', 'June-August - Northern Serengeti'),
            (v_project_id, 'C4', 4, 'C4', 'in_progress', 'September-November - Return migration');
    END IF;

    -- ========================================
    -- SOUTH AFRICA ECOLOGICAL INSTITUTE
    -- ========================================
    INSERT INTO companies (company_name, company_code, contact_email, is_active)
    VALUES (
        'South Africa Ecological Institute',
        'SAEI',
        'research@saei.org.za',
        TRUE
    )
    ON CONFLICT (company_code) DO UPDATE SET company_name = EXCLUDED.company_name
    RETURNING id INTO v_south_africa_eco_id;

    -- South Africa Users
    INSERT INTO users (company_id, username, email, password_hash, full_name, role, is_active)
    VALUES
        (v_south_africa_eco_id, 'pventer', 'p.venter@saei.org.za', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Pieter Venter', 'admin', TRUE),
        (v_south_africa_eco_id, 'tnaidoo', 't.naidoo@saei.org.za', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Thandi Naidoo', 'user', TRUE)
    ON CONFLICT (username) DO NOTHING;

    -- South Africa Projects
    INSERT INTO projects (company_id, project_name, bucket_name, aws_region, description, is_active)
    VALUES (
        v_south_africa_eco_id,
        'Kruger Lion Acoustics',
        'saei-kruger-lion',
        'eu-west-1',
        'Acoustic monitoring of lion populations and territorial behavior in Kruger National Park',
        TRUE
    )
    ON CONFLICT (project_name) DO NOTHING
    RETURNING id INTO v_project_id;

    IF v_project_id IS NOT NULL THEN
        INSERT INTO cycles (project_id, cycle_name, cycle_number, s3_prefix, status, description)
        VALUES
            (v_project_id, 'C1', 1, 'C1', 'completed', 'Summer 2024 - Breeding season'),
            (v_project_id, 'C2', 2, 'C2', 'in_progress', 'Autumn 2024 - Post-breeding'),
            (v_project_id, 'C3', 3, 'C3', 'pending', 'Winter 2024 - Dry season');
    END IF;

    RAISE NOTICE 'Africa region demo data created successfully';
END $$;

-- ============================================================================
-- LATIN AMERICA REGION
-- ============================================================================

DO $$
DECLARE
    -- Company IDs
    v_amazon_research_id INTEGER;
    v_pantanal_conservation_id INTEGER;
    v_andes_biodiversity_id INTEGER;

    -- Project IDs
    v_project_id INTEGER;
BEGIN
    RAISE NOTICE '==================================================';
    RAISE NOTICE 'Creating Latin America Region Demo Data';
    RAISE NOTICE '==================================================';

    -- ========================================
    -- AMAZON RAINFOREST RESEARCH CENTER (BRAZIL)
    -- ========================================
    INSERT INTO companies (company_name, company_code, contact_email, is_active)
    VALUES (
        'Amazon Rainforest Research Center',
        'ARRC',
        'pesquisa@amazonresearch.br',
        TRUE
    )
    ON CONFLICT (company_code) DO UPDATE SET company_name = EXCLUDED.company_name
    RETURNING id INTO v_amazon_research_id;

    -- Brazil Users
    INSERT INTO users (company_id, username, email, password_hash, full_name, role, is_active)
    VALUES
        (v_amazon_research_id, 'msilva', 'm.silva@amazonresearch.br', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Marina Silva', 'admin', TRUE),
        (v_amazon_research_id, 'rcardoso', 'r.cardoso@amazonresearch.br', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Roberto Cardoso', 'user', TRUE),
        (v_amazon_research_id, 'anascimento', 'a.nascimento@amazonresearch.br', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Ana Nascimento', 'user', TRUE)
    ON CONFLICT (username) DO NOTHING;

    -- Brazil Projects
    INSERT INTO projects (company_id, project_name, bucket_name, aws_region, description, is_active)
    VALUES (
        v_amazon_research_id,
        'Amazon Jaguar Acoustic Survey',
        'arrc-amazon-jaguar',
        'us-east-1',
        'Ultrasonic and audible recorder network for jaguar population monitoring in the Amazon basin',
        TRUE
    )
    ON CONFLICT (project_name) DO NOTHING
    RETURNING id INTO v_project_id;

    IF v_project_id IS NOT NULL THEN
        INSERT INTO cycles (project_id, cycle_name, cycle_number, s3_prefix, status, description)
        VALUES
            (v_project_id, 'C1', 1, 'C1', 'completed', 'Wet season - January-April 2024'),
            (v_project_id, 'C2', 2, 'C2', 'completed', 'Transitional season - May-August 2024'),
            (v_project_id, 'C3', 3, 'C3', 'in_progress', 'Dry season - September-December 2024');
    END IF;

    INSERT INTO projects (company_id, project_name, bucket_name, aws_region, description, is_active)
    VALUES (
        v_amazon_research_id,
        'Tapir Movement Ecology',
        'arrc-tapir-tracking',
        'us-east-1',
        'Camera trap study of lowland tapir movement patterns and habitat use',
        TRUE
    )
    ON CONFLICT (project_name) DO NOTHING
    RETURNING id INTO v_project_id;

    IF v_project_id IS NOT NULL THEN
        INSERT INTO cycles (project_id, cycle_name, cycle_number, s3_prefix, status, description)
        VALUES
            (v_project_id, 'C1', 1, 'C1', 'completed', 'Q1 2024'),
            (v_project_id, 'C2', 2, 'C2', 'in_progress', 'Q2 2024');
    END IF;

    -- ========================================
    -- PANTANAL CONSERVATION ALLIANCE (BRAZIL/PARAGUAY)
    -- ========================================
    INSERT INTO companies (company_name, company_code, contact_email, is_active)
    VALUES (
        'Pantanal Conservation Alliance',
        'PCA',
        'info@pantanalalliance.org',
        TRUE
    )
    ON CONFLICT (company_code) DO UPDATE SET company_name = EXCLUDED.company_name
    RETURNING id INTO v_pantanal_conservation_id;

    -- Pantanal Users
    INSERT INTO users (company_id, username, email, password_hash, full_name, role, is_active)
    VALUES
        (v_pantanal_conservation_id, 'loliveira', 'l.oliveira@pantanalalliance.org', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Lucas Oliveira', 'admin', TRUE),
        (v_pantanal_conservation_id, 'jgonzalez', 'j.gonzalez@pantanalalliance.org', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Julia González', 'user', TRUE)
    ON CONFLICT (username) DO NOTHING;

    -- Pantanal Projects
    INSERT INTO projects (company_id, project_name, bucket_name, aws_region, description, is_active)
    VALUES (
        v_pantanal_conservation_id,
        'Pantanal Hyacinth Macaw Monitoring',
        'pca-hyacinth-macaw',
        'us-east-1',
        'Audio recorder deployment for endangered hyacinth macaw population assessment',
        TRUE
    )
    ON CONFLICT (project_name) DO NOTHING
    RETURNING id INTO v_project_id;

    IF v_project_id IS NOT NULL THEN
        INSERT INTO cycles (project_id, cycle_name, cycle_number, s3_prefix, status, description)
        VALUES
            (v_project_id, 'C1', 1, 'C1', 'completed', 'Breeding season - August-November'),
            (v_project_id, 'C2', 2, 'C2', 'in_progress', 'Post-breeding - December-March');
    END IF;

    -- ========================================
    -- ANDES BIODIVERSITY INSTITUTE (ECUADOR/COLOMBIA)
    -- ========================================
    INSERT INTO companies (company_name, company_code, contact_email, is_active)
    VALUES (
        'Andes Biodiversity Institute',
        'ABI',
        'contacto@andesbiodiversity.org',
        TRUE
    )
    ON CONFLICT (company_code) DO UPDATE SET company_name = EXCLUDED.company_name
    RETURNING id INTO v_andes_biodiversity_id;

    -- Andes Users
    INSERT INTO users (company_id, username, email, password_hash, full_name, role, is_active)
    VALUES
        (v_andes_biodiversity_id, 'cmoreno', 'c.moreno@andesbiodiversity.org', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Carlos Moreno', 'admin', TRUE),
        (v_andes_biodiversity_id, 'sprojas', 's.rojas@andesbiodiversity.org', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Sofía Rojas', 'user', TRUE)
    ON CONFLICT (username) DO NOTHING;

    -- Andes Projects
    INSERT INTO projects (company_id, project_name, bucket_name, aws_region, description, is_active)
    VALUES (
        v_andes_biodiversity_id,
        'Cloud Forest Bird Diversity',
        'abi-cloudforest-birds',
        'us-east-1',
        'Multi-elevation acoustic monitoring of bird communities in Andean cloud forests',
        TRUE
    )
    ON CONFLICT (project_name) DO NOTHING
    RETURNING id INTO v_project_id;

    IF v_project_id IS NOT NULL THEN
        INSERT INTO cycles (project_id, cycle_name, cycle_number, s3_prefix, status, description)
        VALUES
            (v_project_id, 'C1', 1, 'C1', 'completed', 'Dry season - June-September'),
            (v_project_id, 'C2', 2, 'C2', 'in_progress', 'Wet season - October-January'),
            (v_project_id, 'C3', 3, 'C3', 'pending', 'Transitional - February-May');
    END IF;

    RAISE NOTICE 'Latin America region demo data created successfully';
END $$;

-- ============================================================================
-- ASIA REGION
-- ============================================================================

DO $$
DECLARE
    -- Company IDs
    v_thailand_elephant_id INTEGER;
    v_borneo_orangutan_id INTEGER;
    v_india_tiger_id INTEGER;

    -- Project IDs
    v_project_id INTEGER;
BEGIN
    RAISE NOTICE '==================================================';
    RAISE NOTICE 'Creating Asia Region Demo Data';
    RAISE NOTICE '==================================================';

    -- ========================================
    -- THAILAND ELEPHANT FOUNDATION
    -- ========================================
    INSERT INTO companies (company_name, company_code, contact_email, is_active)
    VALUES (
        'Thailand Elephant Foundation',
        'TEF',
        'info@thaielephant.org',
        TRUE
    )
    ON CONFLICT (company_code) DO UPDATE SET company_name = EXCLUDED.company_name
    RETURNING id INTO v_thailand_elephant_id;

    -- Thailand Users
    INSERT INTO users (company_id, username, email, password_hash, full_name, role, is_active)
    VALUES
        (v_thailand_elephant_id, 'sprasertsuk', 's.prasertsuk@thaielephant.org', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Somchai Prasertsuk', 'admin', TRUE),
        (v_thailand_elephant_id, 'nwongpreedee', 'n.wongpreedee@thaielephant.org', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Nisa Wongpreedee', 'user', TRUE)
    ON CONFLICT (username) DO NOTHING;

    -- Thailand Projects
    INSERT INTO projects (company_id, project_name, bucket_name, aws_region, description, is_active)
    VALUES (
        v_thailand_elephant_id,
        'Khao Yai Elephant Communication',
        'tef-khaoyai-elephant',
        'ap-southeast-1',
        'Infrasound and ultrasonic monitoring of elephant social communication in Khao Yai National Park',
        TRUE
    )
    ON CONFLICT (project_name) DO NOTHING
    RETURNING id INTO v_project_id;

    IF v_project_id IS NOT NULL THEN
        INSERT INTO cycles (project_id, cycle_name, cycle_number, s3_prefix, status, description)
        VALUES
            (v_project_id, 'C1', 1, 'C1', 'completed', 'Hot season - March-May 2024'),
            (v_project_id, 'C2', 2, 'C2', 'completed', 'Rainy season - June-October 2024'),
            (v_project_id, 'C3', 3, 'C3', 'in_progress', 'Cool season - November 2024-February 2025');
    END IF;

    -- ========================================
    -- BORNEO ORANGUTAN ALLIANCE
    -- ========================================
    INSERT INTO companies (company_name, company_code, contact_email, is_active)
    VALUES (
        'Borneo Orangutan Alliance',
        'BOA',
        'research@borneorangutan.org',
        TRUE
    )
    ON CONFLICT (company_code) DO UPDATE SET company_name = EXCLUDED.company_name
    RETURNING id INTO v_borneo_orangutan_id;

    -- Borneo Users
    INSERT INTO users (company_id, username, email, password_hash, full_name, role, is_active)
    VALUES
        (v_borneo_orangutan_id, 'awibowo', 'a.wibowo@borneorangutan.org', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Ahmad Wibowo', 'admin', TRUE),
        (v_borneo_orangutan_id, 'mtan', 'm.tan@borneorangutan.org', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Michelle Tan', 'user', TRUE),
        (v_borneo_orangutan_id, 'rsulistyo', 'r.sulistyo@borneorangutan.org', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Rini Sulistyo', 'user', TRUE)
    ON CONFLICT (username) DO NOTHING;

    -- Borneo Projects
    INSERT INTO projects (company_id, project_name, bucket_name, aws_region, description, is_active)
    VALUES (
        v_borneo_orangutan_id,
        'Sabah Orangutan Nest Monitoring',
        'boa-sabah-orangutan',
        'ap-southeast-1',
        'Camera trap network for orangutan nest building behavior and population density estimation',
        TRUE
    )
    ON CONFLICT (project_name) DO NOTHING
    RETURNING id INTO v_project_id;

    IF v_project_id IS NOT NULL THEN
        INSERT INTO cycles (project_id, cycle_name, cycle_number, s3_prefix, status, description)
        VALUES
            (v_project_id, 'C1', 1, 'C1', 'completed', 'Masting season - April-July 2024'),
            (v_project_id, 'C2', 2, 'C2', 'in_progress', 'Non-masting - August-November 2024'),
            (v_project_id, 'C3', 3, 'C3', 'pending', 'Fruit scarcity - December 2024-March 2025');
    END IF;

    INSERT INTO projects (company_id, project_name, bucket_name, aws_region, description, is_active)
    VALUES (
        v_borneo_orangutan_id,
        'Danum Valley Gibbon Acoustics',
        'boa-danum-gibbon',
        'ap-southeast-1',
        'Acoustic monitoring of endangered Bornean gibbon morning calls',
        TRUE
    )
    ON CONFLICT (project_name) DO NOTHING
    RETURNING id INTO v_project_id;

    IF v_project_id IS NOT NULL THEN
        INSERT INTO cycles (project_id, cycle_name, cycle_number, s3_prefix, status, description)
        VALUES
            (v_project_id, 'C1', 1, 'C1', 'completed', 'Baseline study - January-June 2024'),
            (v_project_id, 'C2', 2, 'C2', 'in_progress', 'Extended monitoring - July-December 2024');
    END IF;

    -- ========================================
    -- INDIA TIGER CONSERVATION PROJECT
    -- ========================================
    INSERT INTO companies (company_name, company_code, contact_email, is_active)
    VALUES (
        'India Tiger Conservation Project',
        'ITCP',
        'contact@indiatiger.org',
        TRUE
    )
    ON CONFLICT (company_code) DO UPDATE SET company_name = EXCLUDED.company_name
    RETURNING id INTO v_india_tiger_id;

    -- India Users
    INSERT INTO users (company_id, username, email, password_hash, full_name, role, is_active)
    VALUES
        (v_india_tiger_id, 'rsingh', 'r.singh@indiatiger.org', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Rajesh Singh', 'admin', TRUE),
        (v_india_tiger_id, 'pmenon', 'p.menon@indiatiger.org', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Priya Menon', 'user', TRUE)
    ON CONFLICT (username) DO NOTHING;

    -- India Projects
    INSERT INTO projects (company_id, project_name, bucket_name, aws_region, description, is_active)
    VALUES (
        v_india_tiger_id,
        'Ranthambore Tiger Census',
        'itcp-ranthambore-tiger',
        'ap-south-1',
        'Multi-year camera trap study for individual tiger identification and population monitoring',
        TRUE
    )
    ON CONFLICT (project_name) DO NOTHING
    RETURNING id INTO v_project_id;

    IF v_project_id IS NOT NULL THEN
        INSERT INTO cycles (project_id, cycle_name, cycle_number, s3_prefix, status, description)
        VALUES
            (v_project_id, 'C1', 1, 'C1', 'completed', 'Summer 2024 - Pre-monsoon'),
            (v_project_id, 'C2', 2, 'C2', 'completed', 'Monsoon 2024 - Breeding season'),
            (v_project_id, 'C3', 3, 'C3', 'in_progress', 'Winter 2024-2025 - Post-monsoon'),
            (v_project_id, 'C4', 4, 'C4', 'pending', 'Spring 2025 - Tiger tourism season');
    END IF;

    RAISE NOTICE 'Asia region demo data created successfully';
END $$;

-- ============================================================================
-- EUROPE REGION
-- ============================================================================

DO $$
DECLARE
    -- Company IDs
    v_germany_forest_id INTEGER;
    v_spain_lynx_id INTEGER;
    v_norway_wolf_id INTEGER;

    -- Project IDs
    v_project_id INTEGER;
BEGIN
    RAISE NOTICE '==================================================';
    RAISE NOTICE 'Creating Europe Region Demo Data';
    RAISE NOTICE '==================================================';

    -- ========================================
    -- GERMAN FOREST ECOLOGY CENTER
    -- ========================================
    INSERT INTO companies (company_name, company_code, contact_email, is_active)
    VALUES (
        'German Forest Ecology Center',
        'GFEC',
        'info@waldoekologie.de',
        TRUE
    )
    ON CONFLICT (company_code) DO UPDATE SET company_name = EXCLUDED.company_name
    RETURNING id INTO v_germany_forest_id;

    -- Germany Users
    INSERT INTO users (company_id, username, email, password_hash, full_name, role, is_active)
    VALUES
        (v_germany_forest_id, 'hmüller', 'h.mueller@waldoekologie.de', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Hans Müller', 'admin', TRUE),
        (v_germany_forest_id, 'sschmidt', 's.schmidt@waldoekologie.de', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Sabine Schmidt', 'user', TRUE),
        (v_germany_forest_id, 'kbecker', 'k.becker@waldoekologie.de', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Klaus Becker', 'user', TRUE)
    ON CONFLICT (username) DO NOTHING;

    -- Germany Projects
    INSERT INTO projects (company_id, project_name, bucket_name, aws_region, description, is_active)
    VALUES (
        v_germany_forest_id,
        'Black Forest Bat Monitoring',
        'gfec-blackforest-bats',
        'eu-central-1',
        'Ultrasonic bat detector network across elevation gradient in Schwarzwald',
        TRUE
    )
    ON CONFLICT (project_name) DO NOTHING
    RETURNING id INTO v_project_id;

    IF v_project_id IS NOT NULL THEN
        INSERT INTO cycles (project_id, cycle_name, cycle_number, s3_prefix, status, description)
        VALUES
            (v_project_id, 'C1', 1, 'C1', 'completed', 'Spring migration - April-May 2024'),
            (v_project_id, 'C2', 2, 'C2', 'completed', 'Summer breeding - June-August 2024'),
            (v_project_id, 'C3', 3, 'C3', 'in_progress', 'Autumn migration - September-October 2024'),
            (v_project_id, 'C4', 4, 'C4', 'pending', 'Winter hibernation check - November 2024-February 2025');
    END IF;

    INSERT INTO projects (company_id, project_name, bucket_name, aws_region, description, is_active)
    VALUES (
        v_germany_forest_id,
        'Bavarian Lynx Reintroduction',
        'gfec-bavaria-lynx',
        'eu-central-1',
        'Camera trap monitoring of reintroduced Eurasian lynx in Bavarian Forest National Park',
        TRUE
    )
    ON CONFLICT (project_name) DO NOTHING
    RETURNING id INTO v_project_id;

    IF v_project_id IS NOT NULL THEN
        INSERT INTO cycles (project_id, cycle_name, cycle_number, s3_prefix, status, description)
        VALUES
            (v_project_id, 'C1', 1, 'C1', 'completed', 'Post-release - January-April 2024'),
            (v_project_id, 'C2', 2, 'C2', 'in_progress', 'Territory establishment - May-August 2024');
    END IF;

    -- ========================================
    -- IBERIAN LYNX FOUNDATION (SPAIN/PORTUGAL)
    -- ========================================
    INSERT INTO companies (company_name, company_code, contact_email, is_active)
    VALUES (
        'Iberian Lynx Foundation',
        'ILF',
        'info@linceiberico.org',
        TRUE
    )
    ON CONFLICT (company_code) DO UPDATE SET company_name = EXCLUDED.company_name
    RETURNING id INTO v_spain_lynx_id;

    -- Spain Users
    INSERT INTO users (company_id, username, email, password_hash, full_name, role, is_active)
    VALUES
        (v_spain_lynx_id, 'jgarcia', 'j.garcia@linceiberico.org', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'José García', 'admin', TRUE),
        (v_spain_lynx_id, 'mrodriguez', 'm.rodriguez@linceiberico.org', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'María Rodríguez', 'user', TRUE)
    ON CONFLICT (username) DO NOTHING;

    -- Spain Projects
    INSERT INTO projects (company_id, project_name, bucket_name, aws_region, description, is_active)
    VALUES (
        v_spain_lynx_id,
        'Doñana Lynx Recovery Program',
        'ilf-donana-lynx',
        'eu-west-1',
        'Long-term camera trap monitoring of critically endangered Iberian lynx population recovery',
        TRUE
    )
    ON CONFLICT (project_name) DO NOTHING
    RETURNING id INTO v_project_id;

    IF v_project_id IS NOT NULL THEN
        INSERT INTO cycles (project_id, cycle_name, cycle_number, s3_prefix, status, description)
        VALUES
            (v_project_id, 'C1', 1, 'C1', 'completed', 'Breeding season - December 2023-March 2024'),
            (v_project_id, 'C2', 2, 'C2', 'completed', 'Kitten emergence - April-June 2024'),
            (v_project_id, 'C3', 3, 'C3', 'in_progress', 'Juvenile dispersal - July-September 2024'),
            (v_project_id, 'C4', 4, 'C4', 'pending', 'Adult monitoring - October-December 2024');
    END IF;

    -- ========================================
    -- NORWEGIAN WOLF MONITORING PROJECT
    -- ========================================
    INSERT INTO companies (company_name, company_code, contact_email, is_active)
    VALUES (
        'Norwegian Wolf Monitoring Project',
        'NWMP',
        'kontakt@ulveprosjekt.no',
        TRUE
    )
    ON CONFLICT (company_code) DO UPDATE SET company_name = EXCLUDED.company_name
    RETURNING id INTO v_norway_wolf_id;

    -- Norway Users
    INSERT INTO users (company_id, username, email, password_hash, full_name, role, is_active)
    VALUES
        (v_norway_wolf_id, 'lhansen', 'l.hansen@ulveprosjekt.no', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Lars Hansen', 'admin', TRUE),
        (v_norway_wolf_id, 'eolsen', 'e.olsen@ulveprosjekt.no', '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS', 'Elin Olsen', 'user', TRUE)
    ON CONFLICT (username) DO NOTHING;

    -- Norway Projects
    INSERT INTO projects (company_id, project_name, bucket_name, aws_region, description, is_active)
    VALUES (
        v_norway_wolf_id,
        'Scandinavian Wolf Pack Dynamics',
        'nwmp-wolf-packs',
        'eu-north-1',
        'Acoustic howl monitoring and camera traps for wolf pack territory and social structure analysis',
        TRUE
    )
    ON CONFLICT (project_name) DO NOTHING
    RETURNING id INTO v_project_id;

    IF v_project_id IS NOT NULL THEN
        INSERT INTO cycles (project_id, cycle_name, cycle_number, s3_prefix, status, description)
        VALUES
            (v_project_id, 'C1', 1, 'C1', 'completed', 'Winter 2024 - Snow tracking season'),
            (v_project_id, 'C2', 2, 'C2', 'completed', 'Spring 2024 - Denning season'),
            (v_project_id, 'C3', 3, 'C3', 'in_progress', 'Summer 2024 - Pup rearing'),
            (v_project_id, 'C4', 4, 'C4', 'pending', 'Autumn 2024 - Pack reformation');
    END IF;

    RAISE NOTICE 'Europe region demo data created successfully';
END $$;

-- ============================================================================
-- SUMMARY STATISTICS
-- ============================================================================

DO $$
DECLARE
    v_total_companies INTEGER;
    v_total_users INTEGER;
    v_total_projects INTEGER;
    v_total_cycles INTEGER;
BEGIN
    RAISE NOTICE '==================================================';
    RAISE NOTICE 'DEMO DATA CREATION SUMMARY';
    RAISE NOTICE '==================================================';

    SELECT COUNT(*) INTO v_total_companies FROM companies WHERE company_code != 'DEFAULT';
    SELECT COUNT(*) INTO v_total_users FROM users WHERE username != 'admin';
    SELECT COUNT(*) INTO v_total_projects FROM projects;
    SELECT COUNT(*) INTO v_total_cycles FROM cycles;

    RAISE NOTICE 'Total Demo Companies Created: %', v_total_companies;
    RAISE NOTICE 'Total Demo Users Created: %', v_total_users;
    RAISE NOTICE 'Total Projects Created: %', v_total_projects;
    RAISE NOTICE 'Total Cycles Created: %', v_total_cycles;
    RAISE NOTICE '';
    RAISE NOTICE 'Regional Breakdown:';
    RAISE NOTICE '  • Africa: 3 companies (Kenya, Tanzania, South Africa)';
    RAISE NOTICE '  • Latin America: 3 companies (Brazil, Brazil/Paraguay, Ecuador/Colombia)';
    RAISE NOTICE '  • Asia: 3 companies (Thailand, Borneo, India)';
    RAISE NOTICE '  • Europe: 3 companies (Germany, Spain/Portugal, Norway)';
    RAISE NOTICE '';
    RAISE NOTICE 'Default Password for All Demo Users: admin123';
    RAISE NOTICE 'IMPORTANT: Change all passwords in production!';
    RAISE NOTICE '==================================================';
END $$;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Show all companies by region
SELECT
    company_name,
    company_code,
    contact_email,
    CASE
        WHEN company_code IN ('KWT', 'TCN', 'SAEI') THEN 'Africa'
        WHEN company_code IN ('ARRC', 'PCA', 'ABI') THEN 'Latin America'
        WHEN company_code IN ('TEF', 'BOA', 'ITCP') THEN 'Asia'
        WHEN company_code IN ('GFEC', 'ILF', 'NWMP') THEN 'Europe'
        ELSE 'Other'
    END as region,
    (SELECT COUNT(*) FROM users u WHERE u.company_id = c.id) as user_count,
    (SELECT COUNT(*) FROM projects p WHERE p.company_id = c.id) as project_count,
    is_active,
    created_at
FROM companies c
WHERE company_code != 'DEFAULT'
ORDER BY
    CASE
        WHEN company_code IN ('KWT', 'TCN', 'SAEI') THEN 1
        WHEN company_code IN ('ARRC', 'PCA', 'ABI') THEN 2
        WHEN company_code IN ('TEF', 'BOA', 'ITCP') THEN 3
        WHEN company_code IN ('GFEC', 'ILF', 'NWMP') THEN 4
    END,
    company_name;

-- Show project summary
SELECT
    c.company_name,
    c.company_code,
    p.project_name,
    p.bucket_name,
    p.aws_region,
    (SELECT COUNT(*) FROM cycles cy WHERE cy.project_id = p.id) as cycle_count,
    p.is_active
FROM projects p
JOIN companies c ON p.company_id = c.id
ORDER BY c.company_code, p.project_name;
