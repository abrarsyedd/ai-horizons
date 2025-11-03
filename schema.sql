-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS ai_horizons_db;

-- Use the new database
USE ai_horizons_db;

-- Drop tables if they exist to apply new schema
DROP TABLE IF EXISTS contact_submissions;
DROP TABLE IF EXISTS solutions;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS ai_lab_generations; -- Drop the lab table too

-- 1. Services Table
CREATE TABLE services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Solutions Table
CREATE TABLE solutions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Contact Submissions Table
CREATE TABLE contact_submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. AI Lab Generations Table
-- UPDATED: Added ip_address column
CREATE TABLE ai_lab_generations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prompt TEXT NOT NULL,
    ip_address VARCHAR(45), -- For IPv4 or IPv6
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 5. Insert Sample Data for 'services'
-- Truncated descriptions to fit h-[450px] cards
INSERT INTO services (title, description, image_url) VALUES
('Custom AI Development', 'We build, train, and deploy bespoke machine learning models tailored to your unique business challenges, from NLP to predictive analytics.', 'static/img3.png'),
('AI Strategy Consulting', 'Our experts help you identify and prioritize high-impact AI opportunities, creating a comprehensive roadmap for integrating AI into your core business.', 'static/img4.png'),
('Data Engineering & MLOps', 'Build a robust data foundation. We architect scalable data pipelines and implement MLOps practices for reliable, automated machine learning lifecycles.', 'static/img5.png'),
('Generative AI Solutions', 'Harness the power of large language models (LLMs). We create generative AI applications for content creation, code generation, and hyper-personalization.', 'static/img6.png'),
('Computer Vision Systems', 'Unlock insights from images and video. We develop advanced computer vision systems for object detection, image recognition, and real-time video analysis.', 'static/img7.png'),
('AI-Powered Automation', 'Streamline complex processes and boost efficiency. We implement intelligent automation solutions that handle repetitive tasks, allowing your team to focus on strategic work.', 'static/img8.png');

-- 6. Insert Sample Data for 'solutions'
-- Truncated descriptions to fit h-[450px] cards
INSERT INTO solutions (title, description, image_url) VALUES
('AI for Healthcare', 'Enhance patient outcomes with AI-driven diagnostics and personalized treatment plans. We focus on HIPAA-compliant, explainable AI.', 'static/img9.png'),
('AI in Finance & FinTech', 'Combat fraud, optimize trading strategies, and personalize banking with our secure FinTech solutions. We deploy high-speed models for real-time risk assessment.', 'static/img10.png'),
('Retail & E-commerce AI', 'Create hyper-personalized shopping experiences, optimize supply chains, and predict demand with our retail-focused AI. Drive customer loyalty.', 'static/img11.png'),
('Manufacturing & IoT AI', 'Implement predictive maintenance, optimize production lines, and improve quality control with smart factory solutions. We connect your IoT data.', 'static/img12.png'),
('AI for Media & Entertainment', 'Personalize content recommendations, automate post-production workflows, and analyze audience sentiment with our AI tools for the media industry.', 'static/img13.png'),
('AI for Enterprise', 'Empower your organization with custom AI tools. We build internal knowledge bases, automate HR processes, and create intelligent assistants.', 'static/img14.png');

-- End of schema file

