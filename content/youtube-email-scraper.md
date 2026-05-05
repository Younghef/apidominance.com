---
title: "YouTube Instant Email Scraper API"
slug: "youtube-email-scraper"

seo:
  title: "YouTube Email Scraper API — Find Creator Contact Emails Instantly | API Dominance"
  description: "Extract email addresses from any YouTube channel with one API call. Perfect for influencer outreach, brand partnerships, and lead generation. Free tier available."
  keywords:
    - "YouTube email scraper"
    - "YouTube contact finder"
    - "influencer email API"
    - "YouTube channel email"
    - "creator email extractor"
    - "lead generation API"
    - "influencer outreach tool"

accent:
  primary: "#6c2bd9"
  primary_hover: "#5b21c5"
  primary_dark: "#4f46e5"
  hero_gradient_from: "#f5f0ff"
  hero_gradient_to: "#ede9fe"
  hover_bg: "#f5f0ff"
  primary_shadow: "rgba(108,43,217, 0.3)"

hero:
  headline: "Find Any YouTuber's Email in Seconds"
  accent: "Email in Seconds"
  description: "Extract verified email addresses from any YouTube channel with a single API call. Perfect for influencer outreach, brand partnerships, and lead generation."
  subtitle: "Used by marketers, agencies, and developers to automate creator discovery at scale."
  cta_primary: { label: "Try Free on RapidAPI", url: "https://rapidapi.com/derekhefley/api/youtube-instant-email-scraper" }
  cta_secondary: { label: "View on Apify", url: "https://apify.com/derekhefley/youtube-instant-email-scraper" }
  badges: ["99.9% Uptime", "<2s Response", "Free Tier"]

code_example:
  filename: "request.py"
  language: python
  body: |
    # Find emails for any YouTube channel
    import requests

    url = "https://youtube-instant-email-scraper.apidominance.com"
    params = {
        "channel_url": "https://youtube.com/@MrBeast",
        "timeout": 30
    }

    response = requests.get(url, params=params)
    data = response.json()

    print(data["emails"])
    # ["business@mrbeast.com"]

features:
  - { icon: "⚡", title: "Lightning Fast", description: "Get results in under 2 seconds. Our scraper extracts emails directly from channel pages with optimized parsing." }
  - { icon: "🎯", title: "High Accuracy", description: "Verified email extraction from YouTube channel About pages, descriptions, and linked websites. No false positives." }
  - { icon: "🔧", title: "Simple Integration", description: "One endpoint, one parameter. Works with any language — Python, JavaScript, Go, Ruby, PHP. Full OpenAPI spec included." }
  - { icon: "📈", title: "Built for Scale", description: "Handle bulk lookups with consistent performance. Rate limits scale with your plan from 1 to 10 requests per second." }
  - { icon: "🔒", title: "Reliable Infrastructure", description: "Hosted on DigitalOcean with 99.9% uptime SLA. Redis caching for repeat queries. Health monitoring 24/7." }
  - { icon: "💰", title: "Generous Free Tier", description: "50 free requests per month to test and validate. No credit card required. Upgrade only when you're ready." }

params:
  - { name: "channel_url", type: "string", description: "Full URL of the YouTube channel (e.g., \"https://youtube.com/@MrBeast\")", required: true }
  - { name: "timeout",     type: "integer", description: "Request timeout in seconds (default: 30)", required: false }

use_cases:
  - { title: "Influencer Marketing", description: "Automate creator outreach by extracting contact emails from thousands of YouTube channels. Build prospect lists in minutes, not hours." }
  - { title: "Brand Partnerships", description: "Find the right creators for your brand. Get direct email contacts to pitch collaborations without going through agents or middlemen." }
  - { title: "Sales & Lead Gen", description: "Build targeted email lists from YouTube channels in your niche. Perfect for SaaS companies selling to content creators." }
  - { title: "Recruiting & Talent", description: "Reach out to YouTubers for talent management, speaking engagements, or collaboration opportunities with verified contact info." }

response:
  description: "Every response returns a consistent JSON object with the channel name, discovered emails, and source URL. Easy to parse, easy to integrate. No HTML scraping on your end. No regex headaches. Just clean data."
  example_json: |
    // Example API Response
    {
      "channel": "MrBeast",
      "emails": [
        "business@mrbeast.com"
      ],
      "source_url": "https://youtube.com/@MrBeast",
      "scraped_at": "2026-04-13T14:30:00Z",
      "success": true
    }

cta_section:
  headline: "Start Extracting Emails Today"
  body: "50 free requests. No credit card. Results in seconds."
  buttons:
    - { label: "Try Free on RapidAPI", url: "https://rapidapi.com/derekhefley/api/youtube-instant-email-scraper" }
    - { label: "Try on Apify", url: "https://apify.com/derekhefley/youtube-instant-email-scraper" }

tags: [scraping, email, influencer, youtube]
categories: [data]
---

# YouTube Instant Email Scraper

Extract email addresses from any YouTube channel with a single API call.
