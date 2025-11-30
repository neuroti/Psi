# Psi App - Production Deployment Checklist

**Version**: 1.0.0
**Date**: 2025-11-10
**Target Platforms**: Apple App Store, Google Play Store
**Status**: Pre-deployment

---

## Table of Contents

1. [Pre-Deployment Preparation](#1-pre-deployment-preparation)
2. [Backend API Deployment](#2-backend-api-deployment)
3. [iOS App Store Submission](#3-ios-app-store-submission)
4. [Google Play Store Submission](#4-google-play-store-submission)
5. [Security & Compliance](#5-security--compliance)
6. [Testing & Quality Assurance](#6-testing--quality-assurance)
7. [Marketing & Legal](#7-marketing--legal)
8. [Post-Deployment Monitoring](#8-post-deployment-monitoring)
9. [Rollback Plan](#9-rollback-plan)

---

## 1. Pre-Deployment Preparation

### 1.1 Project Configuration

#### Backend Configuration
- [ ] **Environment Variables** - Remove all hardcoded secrets
  - [ ] Generate production `SECRET_KEY` (min 32 characters)
  - [ ] Secure `POSTGRES_PASSWORD` (20+ chars, alphanumeric + symbols)
  - [ ] Configure `CLAUDE_API_KEY` (production key with proper limits)
  - [ ] Set `ACCESS_TOKEN_EXPIRE_HOURS=1` (reduce from 24h to 1h)
  - [ ] Configure `ALLOWED_ORIGINS` for CORS
  - [ ] Set `ENVIRONMENT=production`

  ```bash
  # .env.production (NEVER commit to git)
  SECRET_KEY=$(openssl rand -base64 32)
  POSTGRES_PASSWORD=$(openssl rand -base64 20)
  CLAUDE_API_KEY=sk-ant-api-prod-xxxx
  ACCESS_TOKEN_EXPIRE_HOURS=1
  ALLOWED_ORIGINS=https://api.psi-app.com
  ENVIRONMENT=production
  ```

- [ ] **Database Configuration**
  - [ ] PostgreSQL 15+ production instance configured
  - [ ] MongoDB 7.0+ production cluster ready
  - [ ] Redis 7+ configured for caching
  - [ ] Connection pooling enabled (min: 5, max: 20)
  - [ ] Database backups scheduled (daily automated)
  - [ ] SSL/TLS enabled for all database connections

- [ ] **API Configuration**
  - [ ] Production domain configured: `api.psi-app.com`
  - [ ] SSL certificate installed (Let's Encrypt or commercial)
  - [ ] HTTPS enforced (redirect HTTP to HTTPS)
  - [ ] Rate limiting configured (per security review recommendations)
  - [ ] CORS properly configured for mobile app domains only

#### Mobile App Configuration
- [ ] **Environment Setup**
  - [ ] Production API endpoint: `https://api.psi-app.com/api/v1`
  - [ ] Sentry/crash reporting configured with production DSN
  - [ ] Analytics configured (Firebase/Amplitude)
  - [ ] Push notification certificates/keys configured
  - [ ] Remove all `console.log` statements
  - [ ] Set `__DEV__` checks for development-only features

- [ ] **App Version Management**
  - [ ] Version bumped to 1.0.0 in `package.json`
  - [ ] Build number incremented (iOS: CFBundleVersion, Android: versionCode)
  - [ ] `app.json`/`app.config.js` updated with production config
  - [ ] Version number matches across all platforms

- [ ] **Build Configuration**
  - [ ] iOS: Release scheme configured in Xcode
  - [ ] Android: Release build type configured
  - [ ] ProGuard/R8 enabled for Android (code obfuscation)
  - [ ] JavaScript bundle minified
  - [ ] Source maps uploaded for crash reporting
  - [ ] Remove unused dependencies (run `npm prune --production`)

### 1.2 Code Quality & Review

- [ ] **Code Audit**
  - [ ] All TODO/FIXME comments addressed
  - [ ] No debug code left in production
  - [ ] No test credentials in code
  - [ ] ESLint passes with no errors (`npm run lint`)
  - [ ] TypeScript compilation successful with no errors
  - [ ] Python type checks pass (`mypy backend/app`)
  - [ ] Code coverage > 80% for critical paths

- [ ] **Dependency Audit**
  - [ ] Run `npm audit` and fix all critical/high vulnerabilities
  - [ ] Run `pip-audit` for Python dependencies
  - [ ] All dependencies up to date (security patches)
  - [ ] Remove unused dependencies
  - [ ] License compliance verified for all packages

- [ ] **Performance Optimization**
  - [ ] Images optimized (WebP format where possible)
  - [ ] App size < 50MB (ideally < 30MB)
  - [ ] Cold start time < 3 seconds
  - [ ] API response times < 500ms (p95)
  - [ ] YOLO model optimized (quantization applied)
  - [ ] Database queries optimized (indexes added)
  - [ ] Bundle size analyzed (`expo-optimize` run)

### 1.3 Version Control

- [ ] **Git Repository**
  - [ ] All changes committed and pushed
  - [ ] Production branch created (`release/v1.0.0`)
  - [ ] Tag created: `git tag v1.0.0`
  - [ ] `.env` and secrets NOT in version control
  - [ ] `.gitignore` properly configured
  - [ ] Release notes documented in `CHANGELOG.md`

- [ ] **Deployment Artifacts**
  - [ ] iOS: `.ipa` file built and archived
  - [ ] Android: `.aab` (App Bundle) file generated
  - [ ] Backend: Docker image tagged and pushed to registry
  - [ ] Database migration scripts versioned

---

## 2. Backend API Deployment

### 2.1 Infrastructure Setup

- [ ] **Server Configuration**
  - [ ] Cloud provider chosen (AWS/GCP/Azure)
  - [ ] Production server provisioned (min: 2 vCPUs, 4GB RAM)
  - [ ] Load balancer configured (AWS ALB/GCP LB)
  - [ ] Auto-scaling configured (min: 2, max: 10 instances)
  - [ ] CDN configured for static assets (CloudFront/CloudFlare)
  - [ ] Firewall rules configured (ports 80, 443 only)
  - [ ] DDoS protection enabled

- [ ] **Container Deployment** (Docker)
  - [ ] Docker image built: `docker build -t psi-backend:1.0.0 .`
  - [ ] Image pushed to registry (ECR/GCR/Docker Hub)
  - [ ] Container orchestration configured (ECS/GKE/K8s)
  - [ ] Health checks configured (`/health` endpoint)
  - [ ] Graceful shutdown implemented (SIGTERM handling)
  - [ ] Resource limits set (CPU: 1, Memory: 2GB)

- [ ] **Database Deployment**
  - [ ] PostgreSQL production instance (RDS/Cloud SQL)
  - [ ] MongoDB Atlas cluster (M10+ tier)
  - [ ] Redis ElastiCache/MemoryStore
  - [ ] Automated backups enabled (7-day retention)
  - [ ] Point-in-time recovery enabled
  - [ ] Read replicas configured (if needed)
  - [ ] Connection pooling (PgBouncer/SQLAlchemy pool)

### 2.2 Security Hardening (CRITICAL)

⚠️ **Address all critical vulnerabilities from [AUTHENTICATION_SECURITY_REVIEW.md](../AUTHENTICATION_SECURITY_REVIEW.md)**

- [ ] **Fix #1: Remove Hardcoded SECRET_KEY**
  - [ ] Generate production secret: `openssl rand -base64 32`
  - [ ] Store in environment variable or secrets manager
  - [ ] Add validator to prevent default secret in production
  - [ ] Rotate secret if ever exposed

- [ ] **Fix #2: Implement Token Revocation**
  - [ ] Redis-based token blacklist implemented
  - [ ] Logout endpoint invalidates tokens
  - [ ] Token refresh mechanism implemented
  - [ ] Short-lived access tokens (1 hour)
  - [ ] Longer refresh tokens (7 days)

- [ ] **Fix #3: Implement RBAC (Role-Based Access Control)**
  - [ ] User roles defined: `free`, `premium`, `admin`
  - [ ] Permission system implemented
  - [ ] Endpoint authorization enforced
  - [ ] Admin panel access restricted

- [ ] **Fix #4: Rate Limiting on Auth Endpoints**
  - [ ] Login: 5 attempts per 15 minutes per IP
  - [ ] Register: 3 attempts per hour per IP
  - [ ] Password reset: 3 attempts per hour per email
  - [ ] Token refresh: 10 per hour per user
  - [ ] Redis-based rate limiter (not in-memory)

- [ ] **Fix #5: Reduce Token Expiry**
  - [ ] Access token: 1 hour (was 24 hours)
  - [ ] Refresh token: 7 days
  - [ ] Token rotation on refresh

- [ ] **Fix #6: Account Lockout**
  - [ ] Lock account after 5 failed login attempts
  - [ ] 30-minute lockout period
  - [ ] Email notification sent
  - [ ] Admin unlock capability

- [ ] **Fix #7: Create Authentication Middleware**
  - [ ] `backend/app/api/middleware.py` created
  - [ ] Security headers added (HSTS, CSP, etc.)
  - [ ] Request logging implemented
  - [ ] Rate limiting enforced

- [ ] **Additional Security Measures**
  - [ ] SQL injection protection verified (parameterized queries)
  - [ ] XSS protection (input sanitization)
  - [ ] CSRF protection (SameSite cookies)
  - [ ] File upload validation (max size, type whitelist)
  - [ ] Secrets stored in AWS Secrets Manager/GCP Secret Manager
  - [ ] WAF (Web Application Firewall) enabled

### 2.3 Database Migrations

- [ ] **Pre-Deployment**
  - [ ] Backup production database
  - [ ] Test migrations on staging environment
  - [ ] Rollback plan prepared
  - [ ] Downtime window scheduled (if needed)

- [ ] **Migration Execution**
  - [ ] Run: `alembic upgrade head`
  - [ ] Verify data integrity
  - [ ] Check application health
  - [ ] Monitor error logs

### 2.4 API Testing

- [ ] **Smoke Tests**
  - [ ] Health check endpoint: `GET /health` returns 200
  - [ ] API docs accessible: `GET /docs` returns 200
  - [ ] Authentication works: `POST /api/v1/auth/login`
  - [ ] Food upload works: `POST /api/v1/food/upload`
  - [ ] Rate limiting enforced (test exceeding limits)

- [ ] **Load Testing**
  - [ ] Use Apache JMeter/k6/Locust
  - [ ] Test 1000 concurrent users
  - [ ] Response time p95 < 500ms
  - [ ] Error rate < 0.1%
  - [ ] Database connection pool doesn't exhaust

- [ ] **Integration Tests**
  - [ ] Run full test suite: `pytest tests/integration/ -v`
  - [ ] All tests pass (0 failures)
  - [ ] Database tests pass with production-like data

### 2.5 Monitoring & Logging

- [ ] **Application Monitoring**
  - [ ] APM tool configured (New Relic/Datadog/Sentry)
  - [ ] Error tracking enabled (Sentry)
  - [ ] Uptime monitoring (Pingdom/UptimeRobot)
  - [ ] Custom metrics tracked (API latency, YOLO inference time)

- [ ] **Logging**
  - [ ] Centralized logging (CloudWatch/Stackdriver/ELK)
  - [ ] Log level set to INFO (not DEBUG)
  - [ ] PII/secrets not logged
  - [ ] Request/response logging enabled
  - [ ] Error logs include stack traces

- [ ] **Alerts Configured**
  - [ ] API response time > 1s
  - [ ] Error rate > 1%
  - [ ] CPU usage > 80%
  - [ ] Memory usage > 90%
  - [ ] Disk space < 20%
  - [ ] Database connection failures
  - [ ] SSL certificate expiry (30 days before)

---

## 3. iOS App Store Submission

### 3.1 Apple Developer Account Setup

- [ ] **Account Requirements**
  - [ ] Apple Developer Program enrolled ($99/year)
  - [ ] Organization account (if company) or Individual
  - [ ] Payment information added
  - [ ] Tax forms completed (W-8/W-9)
  - [ ] Banking details for payouts configured

- [ ] **App Store Connect Setup**
  - [ ] App created in App Store Connect
  - [ ] Bundle ID registered: `com.psi.wellness` (or your domain)
  - [ ] App Name: "Psi - Emotion Wellness" (available?)
  - [ ] SKU assigned (unique identifier)
  - [ ] Primary language set (English)
  - [ ] Price tier selected ($0 for free, or premium pricing)

### 3.2 Code Signing & Certificates

- [ ] **Certificates & Profiles**
  - [ ] iOS Distribution Certificate created
  - [ ] App Store provisioning profile created
  - [ ] Push notification certificate configured (APNs)
  - [ ] Certificates installed in Xcode
  - [ ] Team ID configured in `app.json`

- [ ] **Capabilities Enabled** (in Xcode)
  - [ ] Push Notifications
  - [ ] HealthKit (for wellness data)
  - [ ] Camera (for food photos)
  - [ ] Photo Library
  - [ ] Background Modes (if needed)

- [ ] **App Privacy - Data Usage Descriptions** (Info.plist)
  ```xml
  <key>NSCameraUsageDescription</key>
  <string>Psi needs camera access to analyze your food photos for nutrition insights.</string>

  <key>NSPhotoLibraryUsageDescription</key>
  <string>Psi needs photo library access to select food images for analysis.</string>

  <key>NSHealthShareUsageDescription</key>
  <string>Psi reads your heart rate and HRV data to provide personalized emotion-based recommendations.</string>

  <key>NSHealthUpdateUsageDescription</key>
  <string>Psi can save nutrition data to your Health app.</string>
  ```

### 3.3 Build & Archive

- [ ] **Xcode Configuration**
  - [ ] Open project in Xcode: `npx expo run:ios --configuration Release`
  - [ ] Select "Generic iOS Device" as build target
  - [ ] Build configuration set to "Release"
  - [ ] Version and build number updated
  - [ ] Code signing set to "iOS Distribution"
  - [ ] Bitcode enabled (if required)

- [ ] **Archive Creation**
  - [ ] Product → Archive in Xcode
  - [ ] Archive succeeds with no errors
  - [ ] Validate app (Xcode Organizer)
  - [ ] Upload to App Store Connect
  - [ ] Processing completes (check email notification)

- [ ] **TestFlight Beta Testing**
  - [ ] Internal testing group created
  - [ ] Beta build distributed to testers (5-10 people)
  - [ ] Test for 1-2 weeks
  - [ ] Collect and address feedback
  - [ ] Crash reports reviewed and fixed

### 3.4 App Store Listing

- [ ] **App Information**
  - [ ] **App Name**: "Psi - Emotion Wellness"
  - [ ] **Subtitle**: "Food & Mood, Personalized" (max 30 chars)
  - [ ] **Description** (max 4000 chars):
    ```
    Transform your emotional wellness through intelligent food recommendations and real-time emotion monitoring.

    🍽️ AI-POWERED FOOD ANALYSIS
    • Snap photos of your meals for instant nutrition insights
    • 96%+ accuracy food detection powered by YOLO v8
    • Comprehensive breakdown of 62+ nutrients
    • Emotion-based personalized recommendations

    ❤️ REAL-TIME EMOTION TRACKING
    • Connect with Apple HealthKit for heart rate & HRV
    • 8 emotion types analyzed from biometric data
    • Daily wellness score (0-100)
    • Psychology-backed daily wellness tips

    🧠 SMART RECOMMENDATIONS
    • Personalized meal suggestions based on your mood
    • Recipe matching from fridge ingredients
    • Exercise and mindfulness content tailored to emotions
    • Neuroscience-based wellness insights

    📊 COMPREHENSIVE TRACKING
    • Nutrition history and trends
    • Emotion patterns over time
    • Correlate mood with food choices
    • Export data for healthcare providers

    SUBSCRIPTION TIERS:
    • Free: 3 food analyses per day
    • Premium: Unlimited analyses, advanced insights, priority support

    Psi uses cutting-edge AI and neuroscience research to help you understand the connection between food and mood. Take control of your emotional wellness today!
    ```

  - [ ] **Keywords** (max 100 chars): `wellness,emotion,food,nutrition,health,mood,hrv,tracker,ai,mental health`
  - [ ] **Support URL**: `https://psi-app.com/support`
  - [ ] **Marketing URL**: `https://psi-app.com`
  - [ ] **Privacy Policy URL**: `https://psi-app.com/privacy` ⚠️ REQUIRED

- [ ] **Promotional Text** (max 170 chars - can update anytime)
  ```
  🎉 Launch Special: Get 50% off Premium for 3 months! Use code LAUNCH50. Transform your emotional wellness with personalized food insights.
  ```

- [ ] **Screenshots** (Required sizes)
  - [ ] 6.7" Display (iPhone 15 Pro Max): 1290 x 2796 px (3-10 screenshots)
  - [ ] 6.5" Display (iPhone 11 Pro Max): 1242 x 2688 px
  - [ ] 5.5" Display (iPhone 8 Plus): 1242 x 2208 px (optional)
  - [ ] iPad Pro 12.9" (3rd gen): 2048 x 2732 px (if iPad support)

  **Screenshot Recommendations**:
  1. Hero screen - Food analysis in action
  2. Emotion dashboard with wellness score
  3. Recipe recommendations from fridge
  4. Nutrition breakdown details
  5. Wellness trends over time
  6. Premium features highlight

- [ ] **App Preview Videos** (Optional but recommended)
  - [ ] 15-30 second video showcasing key features
  - [ ] Same device sizes as screenshots
  - [ ] No audio required (use captions)

- [ ] **App Icon**
  - [ ] 1024 x 1024 px PNG (no transparency, no rounded corners)
  - [ ] Adheres to Apple's design guidelines
  - [ ] Visually distinctive and recognizable

### 3.5 App Review Information

- [ ] **Contact Information**
  - [ ] First Name / Last Name
  - [ ] Phone Number (must be reachable)
  - [ ] Email Address (monitored daily during review)

- [ ] **Demo Account** (CRITICAL for approval)
  - [ ] Create test account: `reviewer@psi-app.com`
  - [ ] Password: (provide in notes)
  - [ ] Account has Premium access (for full feature review)
  - [ ] Account has sample data (food history, wellness data)
  - [ ] Account doesn't require MFA (or provide instructions)

- [ ] **Notes for Reviewer**
  ```
  Test Account:
  Email: reviewer@psi-app.com
  Password: [SECURE_PASSWORD]

  Testing Instructions:
  1. Login with provided credentials
  2. Grant Camera and HealthKit permissions when prompted
  3. Go to "Food Analysis" tab and upload test food photo (or use camera)
  4. View nutrition breakdown and emotion-based recommendations
  5. Check "Wellness Hub" for real-time emotion insights
  6. View "Fridge Recipes" for recipe recommendations

  Note: HealthKit integration requires actual health data. We've pre-populated the test account with sample emotion data for review purposes.

  For any questions, contact: support@psi-app.com
  ```

### 3.6 Age Rating

- [ ] **Complete Age Rating Questionnaire**
  - Violence: None
  - Profanity or Crude Humor: None
  - Sexual Content: None
  - Nudity: None
  - Cartoon or Fantasy Violence: None
  - Realistic Violence: None
  - Medical/Treatment Information: **YES** (nutrition/wellness data)
  - Alcohol, Tobacco, or Drug Use: None (unless tracking)
  - Gambling: None
  - Horror/Fear Themes: None
  - Mature/Suggestive Themes: None
  - **Expected Rating**: 4+ or 12+ (depending on health data)

### 3.7 Content Rights & Export Compliance

- [ ] **Content Rights**
  - [ ] All images/assets properly licensed or created
  - [ ] No copyrighted material without permission
  - [ ] YOLO model usage complies with license (AGPL-3.0)
  - [ ] Claude API usage complies with Anthropic ToS

- [ ] **Export Compliance**
  - [ ] App uses encryption: **YES** (HTTPS, JWT tokens)
  - [ ] Export compliance form completed
  - [ ] Answer: "No" to proprietary encryption (using standard HTTPS/TLS)

### 3.8 App Privacy Details (CRITICAL - Required by Apple)

⚠️ **Apple requires detailed privacy nutrition labels**

- [ ] **Data Linked to User**
  - [ ] Health & Fitness (HRV, Heart Rate) - Used for emotion analysis
  - [ ] Contact Info (Email) - Account creation
  - [ ] User Content (Food photos) - Analysis purposes
  - [ ] Usage Data (App interactions) - Analytics

- [ ] **Data Not Linked to User**
  - [ ] Diagnostics (Crash logs) - Performance monitoring

- [ ] **Tracking** (cross-app/website tracking)
  - [ ] No (unless using Facebook SDK or similar)

- [ ] **Privacy Policy**
  - [ ] Comprehensive privacy policy written
  - [ ] GDPR compliant (EU users)
  - [ ] CCPA compliant (California users)
  - [ ] HIPAA considerations addressed (health data)
  - [ ] Data retention policy specified
  - [ ] User data deletion process explained
  - [ ] Third-party data sharing disclosed (Claude API, analytics)

### 3.9 Submit for Review

- [ ] **Final Checks**
  - [ ] All required fields completed
  - [ ] Screenshots uploaded for all required sizes
  - [ ] Privacy policy accessible
  - [ ] Demo account verified working
  - [ ] App Store Connect shows "Ready to Submit"

- [ ] **Submit**
  - [ ] Click "Submit for Review"
  - [ ] Confirmation email received
  - [ ] Status changes to "Waiting for Review"
  - [ ] Monitor status daily in App Store Connect

- [ ] **Review Timeline**
  - [ ] Average: 1-3 days (can be up to 1 week)
  - [ ] Respond to any rejections within 24 hours
  - [ ] Address feedback and resubmit

### 3.10 Common Rejection Reasons (Prepare Responses)

- [ ] **Guideline 2.1 - Performance: App Completeness**
  - Ensure app is fully functional
  - No broken features or crashes
  - All placeholder content removed

- [ ] **Guideline 4.2 - Minimum Functionality**
  - App provides sufficient value
  - Not just a website wrapper
  - Native iOS experience

- [ ] **Guideline 5.1.1 - Data Collection and Storage**
  - Privacy policy comprehensive
  - Data usage clearly explained
  - User consent obtained

- [ ] **Guideline 2.3.8 - Metadata**
  - Screenshots accurately represent app
  - No misleading marketing text
  - No competitive references

---

## 4. Google Play Store Submission

### 4.1 Google Play Console Setup

- [ ] **Google Developer Account**
  - [ ] Google Play Developer account created ($25 one-time fee)
  - [ ] Account type selected (Individual or Organization)
  - [ ] Payment profile set up
  - [ ] Tax information completed (W-8/W-9)
  - [ ] Merchant account linked (for in-app purchases)

- [ ] **Create App**
  - [ ] App created in Google Play Console
  - [ ] App name: "Psi - Emotion Wellness"
  - [ ] Default language: English (US)
  - [ ] App or game: App
  - [ ] Free or Paid: Free (with in-app purchases)

### 4.2 Build & Sign Android App

- [ ] **Keystore Creation** (CRITICAL - Backup securely!)
  ```bash
  keytool -genkeypair -v -storetype PKCS12 \
    -keystore psi-release.keystore \
    -alias psi-key-alias \
    -keyalg RSA -keysize 2048 -validity 10000 \
    -storepass [SECURE_PASSWORD] \
    -keypass [SECURE_PASSWORD]
  ```
  - [ ] Keystore file backed up (multiple secure locations)
  - [ ] Passwords stored in password manager
  - [ ] ⚠️ **Cannot recover if lost! Back up securely!**

- [ ] **Configure Gradle** (android/app/build.gradle)
  ```gradle
  android {
      signingConfigs {
          release {
              storeFile file("psi-release.keystore")
              storePassword System.getenv("KEYSTORE_PASSWORD")
              keyAlias "psi-key-alias"
              keyPassword System.getenv("KEY_PASSWORD")
          }
      }
      buildTypes {
          release {
              signingConfig signingConfigs.release
              minifyEnabled true
              proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
          }
      }
  }
  ```

- [ ] **Build Release AAB**
  ```bash
  cd android
  ./gradlew bundleRelease

  # Output: android/app/build/outputs/bundle/release/app-release.aab
  ```
  - [ ] Build succeeds with no errors
  - [ ] AAB file size < 150MB (ideally < 50MB)
  - [ ] ProGuard warnings reviewed and addressed

- [ ] **Google Play App Signing**
  - [ ] Opt in to Google Play App Signing (recommended)
  - [ ] Upload app signing key
  - [ ] Download upload certificate
  - [ ] Keep original keystore as backup

### 4.3 Store Listing

- [ ] **App Details**
  - [ ] **App Name**: "Psi - Emotion Wellness" (max 30 chars)
  - [ ] **Short Description** (max 80 chars):
    ```
    AI-powered food analysis with emotion tracking for personalized wellness
    ```
  - [ ] **Full Description** (max 4000 chars):
    ```
    Transform your emotional wellness through intelligent food recommendations and real-time emotion monitoring.

    🍽️ AI-POWERED FOOD ANALYSIS
    Snap photos of your meals for instant nutrition insights. Our YOLO v8 AI provides 96%+ accuracy food detection with a comprehensive breakdown of 62+ nutrients. Get emotion-based personalized recommendations tailored to your current mood.

    ❤️ REAL-TIME EMOTION TRACKING
    Connect with wearable devices for heart rate & HRV monitoring. Track 8 different emotion types analyzed from your biometric data. Receive a daily wellness score (0-100) and psychology-backed daily wellness tips.

    🧠 SMART RECOMMENDATIONS
    • Personalized meal suggestions based on your current mood
    • Recipe matching from your fridge ingredients
    • Exercise and mindfulness content tailored to your emotions
    • Neuroscience-based wellness insights

    📊 COMPREHENSIVE TRACKING
    • View your nutrition history and trends over time
    • Identify emotion patterns and triggers
    • Correlate mood with food choices
    • Export data for healthcare providers

    💎 SUBSCRIPTION TIERS
    • Free: 3 food analyses per day
    • Premium: Unlimited analyses, advanced insights, priority support

    Psi combines cutting-edge AI and neuroscience research to help you understand the powerful connection between food and mood. Take control of your emotional wellness today!

    PRIVACY & SECURITY
    Your health data is encrypted and never shared without consent. Full privacy policy: https://psi-app.com/privacy

    SUPPORT
    Questions? Contact us at support@psi-app.com
    ```

- [ ] **Graphic Assets**

  **App Icon**
  - [ ] 512 x 512 px PNG (32-bit, no transparency)
  - [ ] Adheres to Material Design guidelines

  **Feature Graphic** (required)
  - [ ] 1024 x 500 px JPG or PNG
  - [ ] No text or logos (Google will overlay)
  - [ ] Visually represents app purpose

  **Phone Screenshots** (2-8 required)
  - [ ] JPEG or 24-bit PNG (no alpha)
  - [ ] Min: 320 px, Max: 3840 px
  - [ ] Portrait or landscape
  - [ ] Recommended: 1080 x 1920 px (Portrait)

  **Screenshot Recommendations**:
  1. Food analysis with nutrition breakdown
  2. Emotion dashboard with wellness score
  3. Recipe recommendations
  4. Wellness trends and insights
  5. Camera/upload interface
  6. Premium features showcase

  **Tablet Screenshots** (optional but recommended if tablet support)
  - [ ] 7-inch: 1080 x 1920 px
  - [ ] 10-inch: 1200 x 1920 px

  **Promo Video** (optional)
  - [ ] YouTube video URL
  - [ ] 30 seconds to 2 minutes
  - [ ] Showcases key features

### 4.4 Categorization & Tags

- [ ] **Category**: Health & Fitness
- [ ] **Tags** (up to 5):
  - Wellness
  - Nutrition
  - Emotion Tracking
  - AI Health
  - Mental Health

- [ ] **Application Type**: App
- [ ] **Store Presence**: Countries/Regions
  - [ ] Select all countries (or target specific regions)
  - [ ] Exclude countries with legal/compliance issues

### 4.5 Content Rating

- [ ] **Complete Questionnaire** (IARC - International Age Rating Coalition)
  - Violence: No
  - Sexual Content: No
  - Profanity: No
  - Controlled Substances: No
  - Gambling: No
  - **Expected Rating**: Everyone / 3+ (or PEGI 3, USK 0)

- [ ] **Review and Submit** rating certificate

### 4.6 Privacy Policy & Data Safety

⚠️ **Google requires detailed Data Safety section**

- [ ] **Privacy Policy URL**: `https://psi-app.com/privacy`
  - [ ] Accessible without login
  - [ ] Covers all data collection and usage

- [ ] **Data Safety Section** (Complete all questions)

  **Data Collection**
  - [ ] Does your app collect or share user data? **YES**

  **Data Types Collected**:
  - [ ] **Health & Fitness**: Heart rate, HRV, biometric data
    - Purpose: App functionality (emotion analysis)
    - Data encrypted in transit & at rest
    - Users can request deletion

  - [ ] **Personal Info**: Email address
    - Purpose: Account management
    - Data encrypted in transit & at rest
    - Users can request deletion

  - [ ] **Photos & Videos**: Food photos
    - Purpose: App functionality (food analysis)
    - Data encrypted in transit & at rest
    - Users can delete

  - [ ] **App Activity**: App interactions, in-app search
    - Purpose: Analytics
    - Data encrypted in transit
    - Not deletable (aggregated analytics)

  **Data Security**
  - [ ] Data encrypted in transit (HTTPS/TLS)
  - [ ] Data encrypted at rest (database encryption)
  - [ ] Users can request data deletion
  - [ ] Data deletion process: Account settings → Delete Account
  - [ ] No data shared with third parties (except Claude API for processing)

### 4.7 App Content & Declarations

- [ ] **Ads**: No (unless implementing AdMob)
- [ ] **In-App Purchases**: YES - Premium subscription
  - [ ] SKU configured in Google Play Console
  - [ ] Pricing tiers set (e.g., $9.99/month, $79.99/year)
  - [ ] Test purchases verified with test accounts

- [ ] **Target Audience**
  - [ ] Primary: Adults 18+
  - [ ] Secondary: Teens 13-17 (if applicable)

- [ ] **COVID-19 Contact Tracing**: No
- [ ] **Government App**: No
- [ ] **Financial Features**: No (unless premium subscriptions count)

### 4.8 Testing & Release Tracks

- [ ] **Internal Testing Track**
  - [ ] Create internal testing group
  - [ ] Add 5-10 tester email addresses
  - [ ] Upload AAB to internal track
  - [ ] Share opt-in URL with testers
  - [ ] Test for 3-5 days

- [ ] **Closed Testing Track** (Optional but recommended)
  - [ ] Create closed testing group (20-50 testers)
  - [ ] Promote from internal testing
  - [ ] Test for 1-2 weeks
  - [ ] Collect feedback via Google Play Console

- [ ] **Open Testing Track** (Optional)
  - [ ] Public beta before full release
  - [ ] Get feedback from wider audience
  - [ ] Address bugs and issues

- [ ] **Production Track**
  - [ ] Promote from testing tracks
  - [ ] Set rollout percentage (start with 10%, increase gradually)
  - [ ] Monitor crash reports and ratings

### 4.9 Submit for Review

- [ ] **Pre-Launch Checklist**
  - [ ] All required fields completed
  - [ ] Graphics uploaded
  - [ ] Privacy policy accessible
  - [ ] Data safety section completed
  - [ ] Content rating obtained
  - [ ] AAB uploaded and validated

- [ ] **Submit**
  - [ ] Click "Send for Review" or "Start Rollout"
  - [ ] Status changes to "Pending Publication"
  - [ ] Review typically takes 1-3 days (faster than iOS)

### 4.10 Pre-Launch Report

- [ ] **Review Pre-Launch Report** (Google automatically tests)
  - [ ] No critical crashes
  - [ ] No performance issues
  - [ ] No security vulnerabilities
  - [ ] Screenshot tests passed
  - [ ] Accessibility tests passed

- [ ] **Address Issues**
  - [ ] Fix any crashes identified
  - [ ] Improve performance if flagged
  - [ ] Re-upload if necessary

---

## 5. Security & Compliance

### 5.1 Security Audit Completion

⚠️ **All critical vulnerabilities from [AUTHENTICATION_SECURITY_REVIEW.md](../AUTHENTICATION_SECURITY_REVIEW.md) MUST be fixed**

- [ ] **Security Review Grade**: Target C- → A (80+/100)
- [ ] All 7 critical vulnerabilities addressed (see section 2.2)
- [ ] Penetration testing performed (OWASP Top 10)
- [ ] Dependency vulnerabilities fixed (`npm audit`, `pip-audit`)
- [ ] Security headers implemented (HSTS, CSP, X-Frame-Options)
- [ ] Input validation on all endpoints
- [ ] Rate limiting enforced
- [ ] HTTPS enforced (no HTTP)
- [ ] Secrets stored securely (AWS Secrets Manager/GCP Secret Manager)

### 5.2 Data Privacy & Compliance

- [ ] **GDPR Compliance** (EU users)
  - [ ] Privacy policy includes GDPR disclosures
  - [ ] User consent obtained before data collection
  - [ ] Right to access: Users can download their data
  - [ ] Right to deletion: Users can delete account and all data
  - [ ] Right to portability: Data export in JSON format
  - [ ] Data Processing Agreement (DPA) if using third-party processors
  - [ ] GDPR representative appointed (if EU-based)
  - [ ] Cookie consent implemented (if using web)

- [ ] **CCPA Compliance** (California users)
  - [ ] "Do Not Sell My Personal Information" link (if applicable)
  - [ ] Privacy policy includes CCPA disclosures
  - [ ] Users can opt-out of data sale (if applicable)
  - [ ] Data deletion requests handled within 45 days

- [ ] **HIPAA Considerations** (Health data)
  - [ ] NOT claiming HIPAA compliance (requires BAA with AWS/GCP)
  - [ ] Privacy policy clarifies app is NOT for medical diagnosis
  - [ ] Disclaimer: "Not a substitute for professional medical advice"
  - [ ] If claiming HIPAA: Business Associate Agreement (BAA) signed
  - [ ] If claiming HIPAA: Audit controls, access controls, encryption

- [ ] **COPPA Compliance** (Children under 13)
  - [ ] App rated 13+ to avoid COPPA requirements
  - [ ] OR: Parental consent mechanism implemented
  - [ ] OR: No data collection from users under 13

- [ ] **Korea-Specific Compliance** (If targeting Korean market)
  - [ ] Personal Information Protection Act (PIPA) compliance
  - [ ] Privacy policy in Korean language
  - [ ] Terms of Service in Korean
  - [ ] Data residency (store Korean user data in Korea if required)

### 5.3 Legal Documents

- [ ] **Privacy Policy** (REQUIRED)
  - [ ] Hosted at: `https://psi-app.com/privacy`
  - [ ] Last updated date included
  - [ ] Covers all data collection and usage
  - [ ] Lists third-party services (Claude API, analytics, hosting)
  - [ ] Explains data retention and deletion
  - [ ] Contact information for privacy inquiries
  - [ ] Plain language (readable by non-lawyers)
  - [ ] Reviewed by legal counsel

- [ ] **Terms of Service** (REQUIRED)
  - [ ] Hosted at: `https://psi-app.com/terms`
  - [ ] User agreements and obligations
  - [ ] Prohibited uses
  - [ ] Limitation of liability
  - [ ] Dispute resolution and governing law
  - [ ] Account termination policy
  - [ ] Intellectual property rights
  - [ ] Reviewed by legal counsel

- [ ] **End User License Agreement (EULA)** (Optional but recommended)
  - [ ] Software license terms
  - [ ] Usage restrictions
  - [ ] Warranty disclaimers

- [ ] **Medical Disclaimer** (CRITICAL for health apps)
  ```
  IMPORTANT: Psi is a wellness app and NOT a medical device.
  The information provided is for informational purposes only
  and is not intended to diagnose, treat, cure, or prevent any
  disease. Always consult with a qualified healthcare provider
  before making any health-related decisions.
  ```
  - [ ] Displayed in app (first launch or settings)
  - [ ] Included in Terms of Service
  - [ ] Prevents liability for medical advice

### 5.4 Third-Party Licenses & Attributions

- [ ] **Open Source Licenses**
  - [ ] YOLO (Ultralytics) - AGPL-3.0 license compliance
    - [ ] App source code released under AGPL (if using AGPL model)
    - [ ] OR: Commercial license obtained from Ultralytics
  - [ ] All npm/pip dependencies reviewed for license compatibility
  - [ ] MIT, Apache 2.0, BSD licenses acknowledged
  - [ ] GPL/AGPL licenses: Source code disclosure requirements met

- [ ] **Third-Party Attributions**
  - [ ] Anthropic Claude API usage complies with ToS
  - [ ] USDA FoodData Central attribution
  - [ ] AI Hub (Korean food dataset) attribution
  - [ ] Icon/image sources credited
  - [ ] Font licenses verified

- [ ] **Attributions Page** in app (Settings → About → Licenses)

---

## 6. Testing & Quality Assurance

### 6.1 Functional Testing

- [ ] **Core Functionality**
  - [ ] User registration works
  - [ ] Login/logout works
  - [ ] Password reset works
  - [ ] Food photo upload works
  - [ ] Food detection accuracy > 95%
  - [ ] Nutrition data displays correctly
  - [ ] Emotion analysis works with real HRV data
  - [ ] Recipe recommendations display
  - [ ] Wellness score calculates correctly
  - [ ] History/trends display correctly

- [ ] **Edge Cases**
  - [ ] No internet connection handling (offline mode)
  - [ ] Poor image quality (blurry photos)
  - [ ] No food detected in image
  - [ ] Empty fridge (no ingredients)
  - [ ] No HealthKit data available
  - [ ] Simultaneous requests (race conditions)
  - [ ] Large image files (10MB+)
  - [ ] Special characters in input fields

### 6.2 Platform-Specific Testing

- [ ] **iOS Testing**
  - [ ] iOS 15, 16, 17 (minimum supported)
  - [ ] iPhone SE (small screen)
  - [ ] iPhone 15 Pro Max (large screen)
  - [ ] iPad (if supported)
  - [ ] Light mode and Dark mode
  - [ ] Landscape and Portrait orientation
  - [ ] Notch/Dynamic Island compatibility
  - [ ] HealthKit integration works
  - [ ] Push notifications work
  - [ ] App Store in-app purchase flow

- [ ] **Android Testing**
  - [ ] Android 10, 11, 12, 13, 14 (minimum API 29)
  - [ ] Small screen device (5.5")
  - [ ] Large screen device (6.7"+)
  - [ ] Tablet (if supported)
  - [ ] Light mode and Dark mode
  - [ ] Various manufacturers (Samsung, Google Pixel, OnePlus)
  - [ ] Google Health Connect integration (if applicable)
  - [ ] Push notifications work
  - [ ] Google Play in-app purchase flow

### 6.3 Performance Testing

- [ ] **App Performance**
  - [ ] Cold start time: < 3 seconds
  - [ ] Screen transition time: < 300ms
  - [ ] Image upload time: < 2 seconds (average)
  - [ ] API response time: < 500ms (p95)
  - [ ] Memory usage: < 200MB
  - [ ] Battery drain: < 5% per hour of active use
  - [ ] App size: < 50MB

- [ ] **Backend Performance**
  - [ ] Load test: 1000 concurrent users
  - [ ] YOLO inference time: < 2 seconds
  - [ ] Database query time: < 100ms (p95)
  - [ ] No memory leaks
  - [ ] Connection pooling working correctly

### 6.4 Security Testing

- [ ] **Penetration Testing**
  - [ ] OWASP Top 10 vulnerabilities tested
  - [ ] SQL injection attempts blocked
  - [ ] XSS attempts blocked
  - [ ] CSRF protection working
  - [ ] JWT token tampering detected
  - [ ] Rate limiting enforced
  - [ ] File upload restrictions enforced

- [ ] **Network Security**
  - [ ] All API calls over HTTPS
  - [ ] Certificate pinning implemented (optional but recommended)
  - [ ] Man-in-the-middle attack prevented
  - [ ] Insecure HTTP blocked

- [ ] **Data Security**
  - [ ] Passwords never logged
  - [ ] Tokens stored securely (iOS Keychain / Android Keystore)
  - [ ] PII not logged in analytics
  - [ ] Database credentials not in source code

### 6.5 Accessibility Testing

- [ ] **iOS Accessibility**
  - [ ] VoiceOver support
  - [ ] Dynamic Type (font scaling)
  - [ ] Color contrast (WCAG AA minimum)
  - [ ] Reduce Motion support
  - [ ] Accessibility labels on all interactive elements

- [ ] **Android Accessibility**
  - [ ] TalkBack support
  - [ ] Font scaling
  - [ ] Color contrast
  - [ ] Touch target size (min 48dp)
  - [ ] Content descriptions on all elements

### 6.6 Localization Testing (If supporting multiple languages)

- [ ] **Language Support**
  - [ ] English (default)
  - [ ] Korean (if target market)
  - [ ] Other languages (Spanish, Japanese, etc.)

- [ ] **Localization**
  - [ ] All strings translated
  - [ ] Date/time formats correct
  - [ ] Currency formats correct
  - [ ] RTL languages supported (if applicable)
  - [ ] Placeholder text translated
  - [ ] Error messages translated

### 6.7 Beta Testing

- [ ] **Internal Beta** (Team members)
  - [ ] 5-10 internal testers
  - [ ] Test for 1 week
  - [ ] Document and fix critical bugs

- [ ] **External Beta** (TestFlight / Play Store Closed Testing)
  - [ ] 50-100 external testers
  - [ ] Recruit via social media, mailing list
  - [ ] Test for 2-4 weeks
  - [ ] Collect feedback via surveys
  - [ ] Monitor crash reports
  - [ ] Fix P0/P1 bugs before launch

- [ ] **Beta Feedback Analysis**
  - [ ] Crash-free rate > 99%
  - [ ] Average rating > 4.0 stars
  - [ ] Major usability issues addressed
  - [ ] Performance issues resolved

---

## 7. Marketing & Legal

### 7.1 Marketing Preparation

- [ ] **Website**
  - [ ] Landing page live: `https://psi-app.com`
  - [ ] App Store / Google Play badges
  - [ ] Feature highlights
  - [ ] Screenshots and demo video
  - [ ] Email signup for launch notification
  - [ ] Blog/press section
  - [ ] FAQ section

- [ ] **Social Media**
  - [ ] Twitter/X account created: `@PsiWellnessApp`
  - [ ] Instagram account: `@psi.wellness`
  - [ ] Facebook page (optional)
  - [ ] LinkedIn company page (for B2B)
  - [ ] Pre-launch posts scheduled (teasers, countdowns)

- [ ] **Press Kit**
  - [ ] App description (short & long versions)
  - [ ] High-res app icon (1024x1024)
  - [ ] Screenshots (all sizes)
  - [ ] Promo video
  - [ ] Founder bios and photos
  - [ ] Press release
  - [ ] Contact information

- [ ] **Launch Strategy**
  - [ ] Launch date chosen (avoid major holidays)
  - [ ] Product Hunt launch planned
  - [ ] Hacker News post prepared
  - [ ] Reddit posts planned (r/apps, r/HealthTech)
  - [ ] Tech blogs contacted (TechCrunch, The Verge, etc.)
  - [ ] Influencers/reviewers contacted
  - [ ] Email blast to beta testers

### 7.2 App Store Optimization (ASO)

- [ ] **Keyword Research**
  - [ ] Primary keywords: wellness, emotion, food, nutrition
  - [ ] Secondary keywords: mood tracker, health app, AI nutrition
  - [ ] Long-tail keywords: emotion-based food recommendations
  - [ ] Competitor analysis (keywords, rankings)

- [ ] **A/B Testing Plan** (Post-launch)
  - [ ] Test different icons
  - [ ] Test different screenshots
  - [ ] Test different description copy
  - [ ] Use App Store Connect / Google Play A/B testing tools

### 7.3 Customer Support

- [ ] **Support Channels**
  - [ ] Email: `support@psi-app.com` (monitored daily)
  - [ ] In-app support/contact form
  - [ ] FAQ/Help Center: `https://psi-app.com/help`
  - [ ] Social media DM support (Twitter, Instagram)
  - [ ] Optional: Live chat (Intercom, Zendesk)

- [ ] **Support Documentation**
  - [ ] Getting started guide
  - [ ] How to upload food photos
  - [ ] How to connect HealthKit/Health Connect
  - [ ] How to interpret wellness scores
  - [ ] Troubleshooting guide
  - [ ] Premium subscription FAQ
  - [ ] Account deletion instructions

- [ ] **Support Team Training**
  - [ ] 1-2 people responsible for support
  - [ ] Response time SLA: < 24 hours
  - [ ] Escalation process for critical issues

### 7.4 Analytics & Attribution

- [ ] **Analytics Setup**
  - [ ] Firebase Analytics / Google Analytics
  - [ ] Custom events tracked:
    - User registration
    - Food photo uploaded
    - Recipe viewed
    - Premium subscription started
    - Daily active users (DAU)
    - Weekly active users (WAU)
    - Retention (Day 1, Day 7, Day 30)

- [ ] **Attribution Tracking**
  - [ ] App Store campaign URLs configured
  - [ ] Google Play campaign URLs configured
  - [ ] Branch.io or AppsFlyer for deep linking (optional)
  - [ ] Track acquisition sources (organic, paid, referral)

- [ ] **Conversion Funnels**
  - [ ] Registration funnel
  - [ ] First photo upload funnel
  - [ ] Premium upgrade funnel
  - [ ] Identify drop-off points

---

## 8. Post-Deployment Monitoring

### 8.1 Launch Day Checklist

- [ ] **Monitoring Setup**
  - [ ] 24/7 on-call rotation scheduled
  - [ ] Status dashboard visible (DataDog/New Relic)
  - [ ] Alerts configured for critical issues
  - [ ] Incident response plan documented

- [ ] **Launch Activities**
  - [ ] Submit launch press release
  - [ ] Post on Product Hunt
  - [ ] Post on Hacker News
  - [ ] Social media launch posts
  - [ ] Email beta testers
  - [ ] Monitor app store reviews
  - [ ] Monitor crash reports
  - [ ] Monitor server metrics

### 8.2 First Week Monitoring

- [ ] **App Store Metrics**
  - [ ] Downloads/installs tracked
  - [ ] Crash-free rate > 99%
  - [ ] App Store rating > 4.0 stars
  - [ ] Review velocity (reviews per day)
  - [ ] Respond to all negative reviews within 24 hours

- [ ] **Backend Metrics**
  - [ ] API uptime > 99.9%
  - [ ] Response time p95 < 500ms
  - [ ] Error rate < 0.1%
  - [ ] Database performance stable
  - [ ] No memory leaks detected
  - [ ] Cost within budget (AWS/GCP bills)

- [ ] **User Behavior**
  - [ ] DAU / MAU ratio
  - [ ] Activation rate (users who complete first photo upload)
  - [ ] Retention Day 1, Day 7
  - [ ] Premium conversion rate
  - [ ] Feature usage (which features most used)

### 8.3 Incident Response

- [ ] **Incident Severity Levels**
  - [ ] **P0 (Critical)**: App down, data breach, payment issues
    - Response: Immediate (< 15 minutes)
    - Fix: < 4 hours
  - [ ] **P1 (High)**: Major feature broken, significant performance degradation
    - Response: < 1 hour
    - Fix: < 24 hours
  - [ ] **P2 (Medium)**: Minor feature broken, cosmetic issues
    - Response: < 4 hours
    - Fix: < 1 week
  - [ ] **P3 (Low)**: Enhancement requests, minor bugs
    - Response: < 1 day
    - Fix: Next release

- [ ] **Incident Procedure**
  1. Detect (alerts, user reports)
  2. Acknowledge (log in incident tracker)
  3. Investigate (gather logs, reproduce)
  4. Fix (deploy hotfix if needed)
  5. Communicate (status page, social media)
  6. Post-mortem (document learnings)

### 8.4 Hotfix Deployment Process

- [ ] **Hotfix Criteria**
  - Critical bugs only (P0/P1)
  - Security vulnerabilities
  - Data loss issues
  - Payment failures

- [ ] **Hotfix Procedure**
  1. Create hotfix branch from production
  2. Implement fix
  3. Test thoroughly
  4. Submit expedited review to App Store (if possible)
  5. Deploy backend immediately
  6. Monitor for 24 hours
  7. Merge back to main branch

- [ ] **Expedited Review** (Apple/Google)
  - Apple: Request via App Store Connect (explain urgency)
  - Google: Usually auto-approved within hours
  - Keep support team informed

### 8.5 User Feedback Loop

- [ ] **Collect Feedback**
  - [ ] In-app feedback form
  - [ ] App Store reviews monitoring
  - [ ] Google Play reviews monitoring
  - [ ] Support email tickets
  - [ ] Social media mentions
  - [ ] User surveys (post-launch)

- [ ] **Respond to Reviews**
  - [ ] Respond to all negative reviews (< 24 hours)
  - [ ] Thank users for positive reviews
  - [ ] Acknowledge bugs and provide timelines
  - [ ] Encourage users to update review after fix

- [ ] **Feature Requests**
  - [ ] Track in product backlog (Jira/Linear/Notion)
  - [ ] Prioritize based on user impact
  - [ ] Communicate roadmap to users

---

## 9. Rollback Plan

### 9.1 Rollback Triggers

- [ ] **Critical Issues Requiring Rollback**
  - Crash rate > 5%
  - Data loss or corruption
  - Security breach
  - Payment system failure
  - Complete feature failure affecting majority of users
  - Legal/compliance violation discovered

### 9.2 Backend Rollback

- [ ] **Database Rollback**
  - [ ] Database backup taken before deployment
  - [ ] Rollback migration scripts prepared
  - [ ] Test rollback on staging first
  - [ ] Execute: `alembic downgrade -1`
  - [ ] Verify data integrity after rollback

- [ ] **Application Rollback**
  - [ ] Previous Docker image tagged and saved
  - [ ] Rollback command: `docker pull psi-backend:1.0.0-prev`
  - [ ] Update load balancer to route to previous version
  - [ ] DNS TTL set low for quick changes
  - [ ] Verify health checks pass

### 9.3 Mobile App Rollback

⚠️ **Cannot force users to rollback - must submit new version**

- [ ] **iOS Rollback Options**
  - [ ] Remove app from sale (temporary)
  - [ ] Submit hotfix version (v1.0.1) with fixes
  - [ ] Request expedited review from Apple
  - [ ] Communicate via in-app message to users

- [ ] **Android Rollback**
  - [ ] Google Play allows staged rollouts (halt rollout)
  - [ ] Roll back to previous version in Play Console
  - [ ] Submit hotfix version
  - [ ] Usually approved within hours

- [ ] **Feature Flags** (Prevention strategy)
  - [ ] Critical features behind feature flags
  - [ ] Can disable remotely without app update
  - [ ] Use LaunchDarkly or custom solution

### 9.4 Communication Plan

- [ ] **Internal Communication**
  - [ ] Notify all team members via Slack/Discord
  - [ ] Update status page (if public)
  - [ ] Log incident in tracker

- [ ] **External Communication**
  - [ ] Social media: "We're aware of issues and working on a fix"
  - [ ] In-app banner (if backend still functional)
  - [ ] Email to affected users (if identifiable)
  - [ ] Update app store description with known issues
  - [ ] Follow up when resolved: "Issue resolved, please update app"

---

## Final Sign-Off

### Pre-Launch Approval

- [ ] **Technical Lead**: All technical requirements met
- [ ] **QA Lead**: All tests passed, no critical bugs
- [ ] **Security Lead**: Security audit passed
- [ ] **Legal**: Privacy policy, ToS reviewed
- [ ] **Product Manager**: Feature complete, ready to launch
- [ ] **CEO/Founder**: Final approval to proceed

**Signatures**:

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Technical Lead | _____________ | ______ | _________ |
| QA Lead | _____________ | ______ | _________ |
| Security Lead | _____________ | ______ | _________ |
| Legal | _____________ | ______ | _________ |
| Product Manager | _____________ | ______ | _________ |
| CEO/Founder | _____________ | ______ | _________ |

---

## Post-Launch Review

**Schedule**: 7 days after launch

- [ ] **Metrics Review**
  - Total downloads: _______
  - DAU/MAU: _______
  - Crash-free rate: _______
  - App Store rating (iOS): _______ stars
  - Play Store rating (Android): _______ stars
  - Premium conversion: _______%
  - API uptime: _______%

- [ ] **Issues Encountered**
  - Number of P0 incidents: _______
  - Number of P1 incidents: _______
  - Average response time: _______
  - Lessons learned: _______________________

- [ ] **Next Steps**
  - [ ] Plan next release (v1.1.0)
  - [ ] Address top user feedback
  - [ ] Optimize conversion funnel
  - [ ] Scale infrastructure if needed

---

## Appendix

### A. Useful Links

- **Apple**
  - App Store Connect: https://appstoreconnect.apple.com
  - Apple Developer: https://developer.apple.com
  - App Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
  - Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines/

- **Google**
  - Google Play Console: https://play.google.com/console
  - Play Store Guidelines: https://play.google.com/about/developer-content-policy/
  - Material Design: https://material.io/design

- **Compliance**
  - GDPR: https://gdpr.eu
  - CCPA: https://oag.ca.gov/privacy/ccpa
  - HIPAA: https://www.hhs.gov/hipaa

### B. Emergency Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| On-Call Engineer | _______ | _______ | _______ |
| CTO/Tech Lead | _______ | _______ | _______ |
| DevOps | _______ | _______ | _______ |
| CEO/Founder | _______ | _______ | _______ |
| Legal Counsel | _______ | _______ | _______ |

### C. Command Cheat Sheet

```bash
# Backend Deployment
docker build -t psi-backend:1.0.0 .
docker push registry.example.com/psi-backend:1.0.0
alembic upgrade head

# iOS Build
cd ios
pod install
xcodebuild -workspace Psi.xcworkspace -scheme Psi -configuration Release archive

# Android Build
cd android
./gradlew bundleRelease

# Database Backup
pg_dump psi_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Database Restore
psql psi_db < backup_20250110_120000.sql

# Check Backend Health
curl https://api.psi-app.com/health

# View Logs
docker logs psi-backend -f --tail=100
kubectl logs -f deployment/psi-backend
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-10
**Next Review**: Before next major release

---

## ✅ Status Summary

Use this section to track overall progress:

```
[ ] Backend Deployment (0/X tasks)
[ ] iOS App Store (0/X tasks)
[ ] Google Play Store (0/X tasks)
[ ] Security & Compliance (0/X tasks)
[ ] Testing & QA (0/X tasks)
[ ] Marketing & Legal (0/X tasks)
[ ] Monitoring Setup (0/X tasks)

Overall Progress: ___% Complete
Target Launch Date: ___________
Status: 🟡 In Progress / 🟢 Ready / 🔴 Blocked
```

---

**🚀 Good luck with your launch!**
