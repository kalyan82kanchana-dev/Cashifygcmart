from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ssl


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection (optional for deployment)
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'cashifygcmart')

try:
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    print(f"✅ Connected to MongoDB: {mongo_url}/{db_name}")
except Exception as e:
    print(f"⚠️ MongoDB connection failed: {e}")
    print("Running in demo mode without database")
    client = None
    db = None

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    message: str = "API is working"

class GiftCardSubmission(BaseModel):
    # Personal Information
    firstName: str
    lastName: str
    email: str
    phoneNumber: Optional[str] = ""
    
    # Gift Card Details (simplified for now - you can expand this)
    cards: List[dict]
    
    # Payment Information
    paymentMethod: str
    paypalAddress: Optional[str] = ""
    zelleDetails: Optional[str] = ""
    cashAppTag: Optional[str] = ""
    btcAddress: Optional[str] = ""
    chimeDetails: Optional[str] = ""

# Email Template Functions
def generate_confirmation_email_html(customer_name, reference_number):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thank You for Your Submission</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333333;
            background-color: #f5f7fa;
            padding: 20px 0;
        }}
        .email-container {{
            max-width: 650px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);
            color: white;
            padding: 35px 30px;
            text-align: center;
        }}
        .logo {{
            font-size: 26px;
            font-weight: 800;
            margin-bottom: 8px;
        }}
        .tagline {{
            font-size: 12px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 20px;
        }}
        .header-title {{
            font-size: 24px;
            font-weight: 600;
        }}
        
        /* Content */
        .content {{
            padding: 35px 30px;
        }}
        .greeting {{
            font-size: 22px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 10px;
        }}
        .reference {{
            font-size: 18px;
            font-weight: 600;
            color: #0c4a6e;
            margin-bottom: 25px;
        }}
        .intro-text {{
            font-size: 16px;
            color: #4b5563;
            margin-bottom: 30px;
            line-height: 1.7;
        }}
        
        /* Sections */
        .section {{
            margin-bottom: 35px;
        }}
        .section-header {{
            font-size: 18px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }}
        .section-icon {{
            margin-right: 10px;
            font-size: 20px;
        }}
        .section-content {{
            color: #4b5563;
            line-height: 1.7;
        }}
        
        /* Next Steps List */
        .next-steps-list {{
            margin: 15px 0;
        }}
        .next-step {{
            margin-bottom: 12px;
        }}
        .step-title {{
            font-weight: 600;
            color: #374151;
        }}
        .step-description {{
            color: #6b7280;
            margin-top: 2px;
        }}
        
        /* Guidelines List */
        .guidelines-list {{
            margin: 15px 0;
        }}
        .guideline-item {{
            margin-bottom: 10px;
            display: flex;
            align-items: flex-start;
        }}
        .guideline-title {{
            font-weight: 600;
            color: #374151;
            min-width: 140px;
        }}
        .guideline-text {{
            color: #6b7280;
            flex: 1;
        }}
        
        /* Important Notice */
        .important-notice {{
            background: #fef3c7;
            border: 1px solid #f59e0b;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
        }}
        .important-title {{
            font-weight: 600;
            color: #92400e;
            margin-bottom: 5px;
        }}
        .important-text {{
            color: #78350f;
            font-size: 14px;
        }}
        
        /* Disclaimer */
        .disclaimer {{
            background: #f8fafc;
            border-left: 4px solid #6b7280;
            padding: 15px 20px;
            margin: 20px 0;
            font-size: 14px;
            color: #4b5563;
        }}
        
        /* Closing */
        .closing {{
            margin: 30px 0 20px 0;
            font-size: 16px;
            color: #374151;
        }}
        .signature {{
            margin-top: 25px;
            font-size: 16px;
            color: #374151;
        }}
        
        /* Footer */
        .footer {{
            background: #ffffff;
            padding: 40px 30px;
            border-top: 2px solid #f1f5f9;
        }}
        
        /* Clean Professional Signature Block */
        .signature-block {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 25px;
            border-bottom: 1px solid #e2e8f0;
        }}
        .signature-name {{
            font-size: 20px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 5px;
            font-family: 'Georgia', serif;
        }}
        .signature-title {{
            font-size: 14px;
            color: #64748b;
            font-weight: 500;
            margin-bottom: 20px;
        }}
        
        /* Contact Grid - Clean Layout */
        .contact-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 25px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .contact-block {{
            padding: 15px;
            background: #f8fafc;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }}
        .contact-label {{
            font-size: 11px;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        .contact-value {{
            font-size: 13px;
            font-weight: 600;
            color: #1e293b;
        }}
        .contact-value a {{
            color: #1e293b;
            text-decoration: none;
        }}
        .contact-value a:hover {{
            color: #ec4899;
        }}
        
        /* Simple Trust Line */
        .trust-line {{
            text-align: center;
            margin-bottom: 25px;
            padding: 12px 0;
            background: #f0fdf4;
            border-radius: 6px;
        }}
        .trust-items {{
            font-size: 12px;
            color: #166534;
            font-weight: 500;
        }}
        
        /* Footer Info - Clean Typography */
        .footer-info {{
            text-align: center;
            font-size: 12px;
            color: #64748b;
            line-height: 1.6;
        }}
        .footer-address {{
            margin-bottom: 12px;
            font-weight: 500;
        }}
        .footer-links-clean {{
            margin-bottom: 12px;
        }}
        .footer-links-clean a {{
            color: #64748b;
            text-decoration: none;
            margin: 0 8px;
            font-weight: 500;
        }}
        .footer-links-clean a:hover {{
            color: #ec4899;
        }}
        .footer-copyright {{
            font-weight: 600;
            color: #475569;
        }}
        
        /* Mobile Footer */
        @media (max-width: 600px) {{
            .contact-grid {{
                grid-template-columns: 1fr;
                gap: 15px;
            }}
            .footer {{
                padding: 30px 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Header -->
        <div class="header">
            <div class="logo">Cashifygcmart</div>
            <div class="tagline">Instant Offers, Same-Day Payments</div>
            <div class="header-title">Thank You for Your Submission</div>
        </div>
        
        <!-- Content -->
        <div class="content">
            <div class="greeting">Thank You for Your Submission, {customer_name}</div>
            <div class="reference">Reference Number: {reference_number}</div>
            
            <div class="intro-text">
                Thank you for submitting your gift card details to Cashifygcmart. Below is an update on the current status of your submission.
            </div>
            
            <!-- Current Status -->
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">📋</span>
                    Current Status
                </div>
                <div class="section-content">
                    Our team is currently reviewing the gift card details you provided. This process ensures all submissions meet our standards for accuracy and authenticity. Your cooperation helps us maintain the trust and quality our customers rely on.
                </div>
            </div>
            
            <!-- Next Steps -->
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">📌</span>
                    Next Steps
                </div>
                <div class="next-steps-list">
                    <div class="next-step">
                        <div class="step-title">Notification Timeline:</div>
                        <div class="step-description">You will receive an update within 14 hours. Please check your inbox and spam/junk folders.</div>
                    </div>
                    <div class="next-step">
                        <div class="step-title">If Approved:</div>
                        <div class="step-description">We'll provide redemption details and timelines in the follow-up email.</div>
                    </div>
                    <div class="next-step">
                        <div class="step-title">If Not Approved:</div>
                        <div class="step-description">If no response is received within 8 hours, it may indicate your submission wasn't approved. Contact us for clarification.</div>
                    </div>
                </div>
                
                <div class="important-notice">
                    <div class="important-title">Important:</div>
                    <div class="important-text">Do not use your gift card during the review period to avoid processing issues.</div>
                </div>
            </div>
            
            <!-- Gift Card Submission Guidelines -->
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">📝</span>
                    Gift Card Submission Guidelines
                </div>
                <div class="guidelines-list">
                    <div class="guideline-item">
                        <div class="guideline-title">Eligible Cards:</div>
                        <div class="guideline-text">Only those listed in our Rate Calculator.</div>
                    </div>
                    <div class="guideline-item">
                        <div class="guideline-title">Minimum Value:</div>
                        <div class="guideline-text">$50 per card.</div>
                    </div>
                    <div class="guideline-item">
                        <div class="guideline-title">Processing Times:</div>
                        <div class="guideline-text">Vary based on demand and market conditions.</div>
                    </div>
                    <div class="guideline-item">
                        <div class="guideline-title">Sundays:</div>
                        <div class="guideline-text">Submissions are processed on the next business day.</div>
                    </div>
                    <div class="guideline-item">
                        <div class="guideline-title">After 8 PM EST:</div>
                        <div class="guideline-text">Processed the following day.</div>
                    </div>
                    <div class="guideline-item">
                        <div class="guideline-title">Payment Methods:</div>
                        <div class="guideline-text">May be updated based on transaction success.</div>
                    </div>
                    <div class="guideline-item">
                        <div class="guideline-title">Unlisted Cards:</div>
                        <div class="guideline-text">Contact support before submission.</div>
                    </div>
                </div>
                
                <div class="disclaimer">
                    <strong>Disclaimer:</strong> Cashifygcmart is not responsible for balance discrepancies on unlisted cards.
                </div>
            </div>
            
            <!-- Closing -->
            <div class="closing">
                Thank you again for choosing Cashifygcmart. Our support team is always here to help.
            </div>
            
            <div class="signature">
                Best regards,
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            
            <!-- Clean Signature Block -->
            <div class="signature-block">
                <div class="signature-name">Robert Smith</div>
                <div class="signature-title">Customer Support Manager, Cashifygcmart</div>
            </div>
            
            <!-- Contact Information Grid -->
            <div class="contact-grid">
                <div class="contact-block">
                    <div class="contact-label">Email Support</div>
                    <div class="contact-value">
                        <a href="mailto:support@cashifygcmart.com">support@cashifygcmart.com</a>
                    </div>
                </div>
                
                <div class="contact-block">
                    <div class="contact-label">Phone Support</div>
                    <div class="contact-value">(555) 013-2099</div>
                </div>
                
                <div class="contact-block">
                    <div class="contact-label">Website</div>
                    <div class="contact-value">cashifygcmart.com</div>
                </div>
            </div>
            
            <!-- Trust Indicators - Single Clean Line -->
            <div class="trust-line">
                <div class="trust-items">
                    SSL Secured • Same-Day Payouts • No Hidden Fees • 230+ Vendors Trusted
                </div>
            </div>
            
            <!-- Footer Information -->
            <div class="footer-info">
                <div class="footer-address">
                    2099 Harborview Drive, Suite 210, San Diego, CA 92101
                </div>
                
                <div class="footer-links-clean">
                    Rate Calculator | FAQs | Privacy Policy | Terms of Service
                </div>
                
                <div class="footer-copyright">
                    © 2025 Cashifygcmart. All rights reserved.
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    """
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gift Card Submission Confirmed</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333333;
            background-color: #f5f7fa;
        }}
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);
            color: white;
            padding: 30px 25px;
            text-align: center;
        }}
        .logo {{
            font-size: 24px;
            font-weight: 800;
            margin-bottom: 5px;
        }}
        .tagline {{
            font-size: 11px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .header-title {{
            font-size: 22px;
            font-weight: 600;
            margin-top: 15px;
        }}
        
        /* Content */
        .content {{
            padding: 30px 25px;
        }}
        .greeting {{
            font-size: 18px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 15px;
        }}
        .reference-box {{
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border: 1px solid #0ea5e9;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 25px 0;
        }}
        .reference-label {{
            font-size: 13px;
            color: #0369a1;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .reference-number {{
            font-size: 24px;
            font-weight: 800;
            color: #0c4a6e;
            margin-top: 5px;
        }}
        
        /* Status Section */
        .status-section {{
            background: #f8fafc;
            border-radius: 8px;
            padding: 20px;
            margin: 25px 0;
        }}
        .status-title {{
            font-size: 16px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }}
        .status-icon {{
            width: 20px;
            height: 20px;
            background: #10b981;
            border-radius: 50%;
            margin-right: 10px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
        }}
        
        /* Next Steps */
        .next-steps {{
            margin: 25px 0;
        }}
        .steps-title {{
            font-size: 16px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 15px;
        }}
        .step-item {{
            display: flex;
            margin-bottom: 12px;
            align-items: flex-start;
        }}
        .step-number {{
            background: #ec4899;
            color: white;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 600;
            margin-right: 12px;
            flex-shrink: 0;
        }}
        .step-text {{
            font-size: 14px;
            color: #4b5563;
        }}
        
        /* Important Notice */
        .notice-box {{
            background: #fef3c7;
            border: 1px solid #f59e0b;
            border-radius: 8px;
            padding: 15px;
            margin: 25px 0;
        }}
        .notice-title {{
            font-size: 14px;
            font-weight: 600;
            color: #92400e;
            margin-bottom: 5px;
        }}
        .notice-text {{
            font-size: 13px;
            color: #78350f;
        }}
        
        /* Footer */
        .footer {{
            background: #f8fafc;
            padding: 25px;
            border-top: 1px solid #e2e8f0;
        }}
        .footer-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 15px;
        }}
        .signature {{
            text-align: left;
        }}
        .signature-name {{
            font-size: 16px;
            font-weight: 600;
            color: #1f2937;
        }}
        .signature-title {{
            font-size: 13px;
            color: #6b7280;
        }}
        .contact-info {{
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .contact-item {{
            font-size: 13px;
            color: #ec4899;
            text-decoration: none;
        }}
        .trust-badges {{
            background: #f0fdf4;
            border-radius: 6px;
            padding: 12px;
            text-align: center;
            margin-bottom: 15px;
        }}
        .trust-badges-grid {{
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            font-size: 12px;
            color: #059669;
        }}
        .footer-bottom {{
            text-align: center;
            font-size: 11px;
            color: #6b7280;
            line-height: 1.5;
        }}
        .footer-links {{
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }}
        .footer-link {{
            color: #6b7280;
            text-decoration: none;
            font-size: 11px;
        }}
        
        /* Mobile Responsive */
        @media (max-width: 600px) {{
            .email-container {{
                margin: 0 10px;
                border-radius: 8px;
            }}
            .header, .content, .footer {{
                padding: 20px 15px;
            }}
            .footer-content {{
                flex-direction: column;
                text-align: center;
            }}
            .contact-info {{
                justify-content: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Header -->
        <div class="header">
            <div class="logo">Cashifygcmart</div>
            <div class="tagline">Instant Offers, Same-Day Payments</div>
            <div class="header-title">✅ Submission Confirmed</div>
        </div>
        
        <!-- Content -->
        <div class="content">
            <div class="greeting">Hi {customer_name},</div>
            
            <p style="color: #4b5563; margin-bottom: 20px;">
                Thank you for choosing Cashifygcmart! We've successfully received your gift card submission and our team is already reviewing it.
            </p>
            
            <!-- Reference Number -->
            <div class="reference-box">
                <div class="reference-label">Your Reference Number</div>
                <div class="reference-number">{reference_number}</div>
                <div style="font-size: 12px; color: #0369a1; margin-top: 5px;">Save this for your records</div>
            </div>
            
            <!-- Current Status -->
            <div class="status-section">
                <div class="status-title">
                    <div class="status-icon">✓</div>
                    Current Status: Under Review
                </div>
                <p style="color: #6b7280; font-size: 14px;">
                    Our verification team is checking your gift card details for authenticity and accuracy. This process ensures secure transactions for everyone.
                </p>
            </div>
            
            <!-- What Happens Next -->
            <div class="next-steps">
                <div class="steps-title">What Happens Next:</div>
                
                <div class="step-item">
                    <div class="step-number">1</div>
                    <div class="step-text">
                        <strong>Verification (2-4 hours):</strong> We'll verify your gift card balance and authenticity.
                    </div>
                </div>
                
                <div class="step-item">
                    <div class="step-number">2</div>
                    <div class="step-text">
                        <strong>Approval & Payment:</strong> Once approved, we'll process your payment via your chosen method.
                    </div>
                </div>
                
                <div class="step-item">
                    <div class="step-number">3</div>
                    <div class="step-text">
                        <strong>Confirmation:</strong> You'll receive an email confirmation once payment is sent.
                    </div>
                </div>
            </div>
            
            <!-- Important Notice -->
            <div class="notice-box">
                <div class="notice-title">⚠️ Important:</div>
                <div class="notice-text">
                    Please do not use your gift card while it's under review to avoid any processing issues.
                </div>
            </div>
            
            <p style="color: #4b5563; margin-top: 20px;">
                Questions? Simply reply to this email or contact our support team. We'll update you within 14 hours!
            </p>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <div class="footer-content">
                <div class="signature">
                    <div class="signature-name">Robert Smith</div>
                    <div class="signature-title">Customer Support Manager</div>
                </div>
                
                <div class="contact-info">
                    <a href="mailto:support@cashifygcmart.com" class="contact-item">📧 support@cashifygcmart.com</a>
                    <span class="contact-item">📞 (555) 013-2099</span>
                    <a href="https://www.cashifygcmart.com" class="contact-item">🌐 cashifygcmart.com</a>
                </div>
            </div>
            
            <div class="trust-badges">
                <div class="trust-badges-grid">
                    <span>✅ SSL Secured</span>
                    <span>✅ Same-Day Payouts</span>
                    <span>✅ No Hidden Fees</span>
                    <span>✅ 230+ Vendors</span>
                </div>
            </div>
            
            <div class="footer-bottom">
                <div class="footer-links">
                    <a href="https://www.cashifygcmart.com/rate-calculator" class="footer-link">Rate Calculator</a>
                    <a href="https://www.cashifygcmart.com/faqs" class="footer-link">FAQs</a>
                    <a href="https://www.cashifygcmart.com/privacy-policy" class="footer-link">Privacy</a>
                    <a href="https://www.cashifygcmart.com/terms-of-service" class="footer-link">Terms</a>
                </div>
                
                <div>📍 2099 Harborview Drive, Suite 210, San Diego, CA 92101</div>
                <div style="margin-top: 8px;">© 2025 Cashifygcmart. All rights reserved.</div>
            </div>
        </div>
    </div>
</body>
</html>
    """
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Submission Received — Reference {reference_number}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background-color: #f9fafb;
            padding: 20px 0;
        }}
        .email-container {{
            max-width: 650px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 50%, #ec4899 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .logo {{
            font-size: 28px;
            font-weight: 800;
            margin-bottom: 8px;
        }}
        .tagline {{
            font-size: 12px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .header h1 {{
            margin-top: 20px;
            font-size: 24px;
            font-weight: 600;
        }}
        
        /* Content */
        .content {{
            padding: 40px 30px;
        }}
        
        /* Text Styling */
        .greeting {{
            font-size: 18px;
            margin-bottom: 20px;
            color: #1f2937;
        }}
        
        .intro-text {{
            margin-bottom: 30px;
            color: #374151;
            font-size: 16px;
        }}
        
        .reference-highlight {{
            font-weight: 700;
            color: #ec4899;
        }}
        
        /* Section Headers */
        .section-header {{
            font-size: 20px;
            font-weight: 700;
            color: #1f2937;
            margin: 35px 0 20px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #ec4899;
        }}
        
        .section-text {{
            margin-bottom: 25px;
            color: #374151;
            font-size: 16px;
        }}
        
        /* Lists */
        .content-list {{
            margin: 20px 0;
            padding-left: 0;
            list-style: none;
        }}
        
        .content-list li {{
            margin-bottom: 15px;
            padding-left: 20px;
            position: relative;
            color: #374151;
            font-size: 16px;
        }}
        
        .content-list li::before {{
            content: "•";
            color: #ec4899;
            font-weight: bold;
            position: absolute;
            left: 0;
            font-size: 18px;
        }}
        
        .list-title {{
            font-weight: 600;
            color: #1f2937;
        }}
        
        /* Important Notice */
        .important-notice {{
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            border: 2px solid #f87171;
            border-radius: 12px;
            padding: 20px;
            margin: 25px 0;
        }}
        
        .important-text {{
            color: #7f1d1d;
            font-weight: 600;
            font-size: 16px;
        }}
        
        /* Disclaimer */
        .disclaimer {{
            background: #fef7ee;
            border-left: 4px solid #f59e0b;
            padding: 15px 20px;
            margin: 25px 0;
            font-style: italic;
            color: #92400e;
            font-size: 15px;
        }}
        
        /* Closing */
        .closing {{
            margin: 35px 0 25px 0;
            color: #374151;
            font-size: 16px;
        }}
        
        .closing-thanks {{
            margin: 25px 0;
            color: #374151;
            font-size: 16px;
        }}
        
        /* Footer */
        .footer {{
            background: #ffffff;
            color: #1f2937;
            padding: 40px 30px;
            text-align: center;
            border-top: 1px solid #e5e7eb;
        }}
        .signature {{
            margin-bottom: 30px;
        }}
        .signature-name {{
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 6px;
            color: #1f2937;
        }}
        .signature-title {{
            color: #6b7280;
            font-size: 16px;
            font-weight: 500;
        }}
        .contact-section {{
            margin: 30px 0;
        }}
        .contact-info {{
            display: flex;
            justify-content: center;
            gap: 40px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }}
        .contact-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: #374151;
            text-decoration: none;
            font-size: 15px;
            font-weight: 500;
            transition: color 0.3s ease;
        }}
        .contact-item:hover {{
            color: #ec4899;
        }}
        .contact-icon {{
            width: 18px;
            height: 18px;
            opacity: 0.7;
        }}
        .footer-divider {{
            width: 60px;
            height: 2px;
            background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);
            margin: 20px auto;
            border-radius: 1px;
        }}
        .footer-note {{
            font-size: 13px;
            color: #6b7280;
            line-height: 1.6;
            max-width: 400px;
            margin: 0 auto;
        }}
        .footer-note a {{
            color: #ec4899;
            font-weight: 500;
            text-decoration: none;
        }}
        .footer-note a:hover {{
            text-decoration: underline;
        }}
        .copyright {{
            margin-bottom: 8px;
            font-weight: 500;
        }}
        
        /* Links */
        a {{
            color: #ec4899;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        
        /* Mobile Responsive */
        @media (max-width: 640px) {{
            .email-container {{
                margin: 0 10px;
                border-radius: 12px;
            }}
            .header, .content, .footer {{
                padding: 24px 20px;
            }}
            .contact-info {{
                flex-direction: column;
                gap: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Header -->
        <div class="header">
            <div class="logo">Cashifygcmart</div>
            <div class="tagline">Instant Offers, Same-Day Payments</div>
            <h1>Submission Received</h1>
        </div>
        
        <!-- Content -->
        <div class="content">
            <!-- Greeting and Introduction -->
            <div class="greeting">Hi {customer_name},</div>
            
            <div class="intro-text">
                Thanks — we've received your gift card submission. Your reference number is <span class="reference-highlight">{reference_number}</span>. Below is the current status and what to expect next.
            </div>
            
            <!-- Current Status -->
            <h2 class="section-header">Current status</h2>
            <div class="section-text">
                Our team is reviewing the gift card details you submitted to confirm accuracy and authenticity. This verification helps us keep the process safe and reliable for everyone.
            </div>
            
            <!-- Next Steps -->
            <h2 class="section-header">Next steps</h2>
            <ul class="content-list">
                <li><span class="list-title">When you'll hear from us:</span> Expect an update within 14 hours. Please check your inbox (and spam/junk folder).</li>
                <li><span class="list-title">If approved:</span> We'll email redemption instructions and the payout timeline.</li>
                <li><span class="list-title">If not approved:</span> You'll receive an explanation. If you still haven't heard from us 8 hours after the 14-hour window, please contact support so we can follow up.</li>
            </ul>
            
            <!-- Important Notice -->
            <div class="important-notice">
                <div class="important-text">Important: Please do not use the gift card while it's under review to avoid processing issues.</div>
            </div>
            
            <!-- Submission Guidelines -->
            <h2 class="section-header">Submission guidelines & processing</h2>
            <ul class="content-list">
                <li><span class="list-title">Eligible cards:</span> Only cards listed in our Rate Calculator are accepted.</li>
                <li><span class="list-title">Minimum value:</span> $50 per card.</li>
                <li><span class="list-title">Processing times:</span> Vary depending on demand and market conditions.</li>
                <li><span class="list-title">Sundays & late submissions:</span> Submissions on Sundays or after 8:00 PM EST are processed the next business day.</li>
                <li><span class="list-title">Payment methods:</span> Payout method may change depending on transaction outcome.</li>
                <li><span class="list-title">Unlisted cards:</span> Contact support before submitting cards not shown in the Rate Calculator.</li>
            </ul>
            
            <!-- Disclaimer -->
            <div class="disclaimer">
                <strong>Disclaimer:</strong> CashifyGCmart is not responsible for balance discrepancies on unlisted cards.
            </div>
            
            <!-- Closing Message -->
            <div class="closing">
                If you have questions or need help, reply to this email or contact our support team.
            </div>
            
            <div class="closing-thanks">
                Thanks for choosing CashifyGCmart — we'll be in touch soon.
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <!-- Compact Professional Footer -->
            <div style="background: #f8fafc; padding: 25px 20px; border-radius: 8px; text-align: center;">
                
                <!-- Signature & Contact in One Row -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 15px;">
                    <div style="text-align: left;">
                        <div style="font-size: 18px; font-weight: 700; color: #1f2937; margin-bottom: 3px;">Robert Smith</div>
                        <div style="font-size: 14px; color: #6b7280;">Customer Support Manager</div>
                    </div>
                    
                    <div style="display: flex; gap: 20px; align-items: center; flex-wrap: wrap;">
                        <a href="mailto:support@cashifygcmart.com" style="color: #ec4899; text-decoration: none; font-size: 13px;">
                            📧 support@cashifygcmart.com
                        </a>
                        <span style="color: #ec4899; font-size: 13px;">📞 (555) 013-2099</span>
                        <a href="https://www.cashifygcmart.com" style="color: #ec4899; text-decoration: none; font-size: 13px;">
                            🌐 cashifygcmart.com
                        </a>
                    </div>
                </div>
                
                <!-- Compact Trust Badges -->
                <div style="background: #f0fdf4; padding: 12px; border-radius: 6px; margin-bottom: 15px;">
                    <div style="display: flex; justify-content: center; gap: 25px; flex-wrap: wrap; font-size: 12px; color: #059669;">
                        <span>✅ SSL Secured</span>
                        <span>✅ Same-Day Payouts</span>
                        <span>✅ No Hidden Fees</span>
                        <span>✅ 230+ Vendors</span>
                    </div>
                </div>
                
                <!-- Address & Legal Links in One Line -->
                <div style="font-size: 11px; color: #6b7280; line-height: 1.4;">
                    <div style="margin-bottom: 8px;">
                        📍 2099 Harborview Drive, Suite 210, San Diego, CA 92101
                    </div>
                    
                    <div style="display: flex; justify-content: center; gap: 12px; flex-wrap: wrap; margin-bottom: 8px;">
                        <a href="https://www.cashifygcmart.com/rate-calculator" style="color: #6b7280; text-decoration: none;">Rate Calculator</a>
                        <span>•</span>
                        <a href="https://www.cashifygcmart.com/faqs" style="color: #6b7280; text-decoration: none;">FAQs</a>
                        <span>•</span>
                        <a href="https://www.cashifygcmart.com/privacy-policy" style="color: #6b7280; text-decoration: none;">Privacy</a>
                        <span>•</span>
                        <a href="https://www.cashifygcmart.com/terms-of-service" style="color: #6b7280; text-decoration: none;">Terms</a>
                    </div>
                    
                    <div>
                        © 2025 Cashifygcmart. All rights reserved. | Add support@cashifygcmart.com to your contacts.
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    """

# Generate unique reference number
def generate_reference_number():
    timestamp = datetime.now().strftime("%H%M%S")
    random_num = random.randint(10, 99)
    return f"GC-{timestamp}-{random_num}"

# Resend email sending function for customer confirmation
async def send_confirmation_email(email: str, customer_name: str, reference_number: str):
    try:
        # Get SMTP settings from environment
        smtp_server = os.environ.get('SMTP_SERVER')
        smtp_port = int(os.environ.get('SMTP_PORT', 465))
        smtp_username = os.environ.get('SMTP_USERNAME')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        use_ssl = os.environ.get('SMTP_USE_SSL', 'true').lower() == 'true'
        
        if not all([smtp_server, smtp_username, smtp_password]):
            print("ERROR: SMTP settings not found in environment variables")
            return False
        
        # Generate email content
        email_html = generate_confirmation_email_html(customer_name, reference_number)
        subject = f"Gift Card Submission Confirmation - Reference #{reference_number}"
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = smtp_username
        msg['To'] = email
        msg['Subject'] = subject
        
        # Add HTML content
        html_part = MIMEText(email_html, 'html')
        msg.attach(html_part)
        
        # Send email via SMTP
        if use_ssl:
            # SSL connection
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
        else:
            # TLS connection
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
        
        print(f"✅ Customer confirmation email sent to: {email}")
        print(f"Reference Number: {reference_number}")
        return True
        
    except Exception as e:
        print(f"❌ SMTP email sending failed: {e}")
        return False

# Internal notification email template for operations team with images
def generate_internal_notification_email(customer_name, reference_number, submission_data):
    cards_info = ""
    total_value = 0
    
    for i, card in enumerate(submission_data.get('cards', []), 1):
        card_value = float(card.get('value', 0)) if card.get('value', '').replace('.', '').isdigit() else 0
        total_value += card_value
        
        # Simple card info without complex formatting
        cards_info += f"""
        Card {i}: {card.get('brand', 'N/A')} - Value: {card.get('value', '0')} - Condition: {card.get('condition', 'N/A').replace('-', ' ').title()}
        Receipt: {"Yes" if card.get('hasReceipt') == 'yes' else "No"} - Type: {card.get('cardType', 'N/A').title()}"""
        
        # Add digital card details if it's a digital card
        if card.get('cardType') == 'digital':
            digital_code = card.get('digitalCode', 'N/A')
            digital_pin = card.get('digitalPin', 'Not provided')
            cards_info += f"""
        Digital Code: {digital_code}
        Digital PIN: {digital_pin}"""
        
        cards_info += "\n"
    
    # Payment method details
    payment_method = submission_data.get('paymentMethod', '').upper()
    payment_details = ""
    if payment_method == 'PAYPAL':
        payment_details = f"PayPal: {submission_data.get('paypalAddress', 'Not provided')}"
    elif payment_method == 'ZELLE':
        payment_details = f"Zelle: {submission_data.get('zelleDetails', 'Not provided')}"
    elif payment_method == 'CASHAPP':
        payment_details = f"Cash App: {submission_data.get('cashAppTag', 'Not provided')}"
    elif payment_method == 'BTC':
        payment_details = f"Bitcoin: {submission_data.get('btcAddress', 'Not provided')}"
    elif payment_method == 'CHIME':
        payment_details = f"Chime: {submission_data.get('chimeDetails', 'Not provided')}"
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>New Customer Submission - {reference_number}</title>
</head>
<body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px;">
        
        <h2 style="color: #1f2937; margin-top: 0;">New Customer Submission</h2>
        
        <div style="background: #e5e7eb; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <strong>Reference Number:</strong> {reference_number}
        </div>
        
        <h3 style="color: #374151; border-bottom: 2px solid #e5e7eb; padding-bottom: 5px;">Customer Information</h3>
        <p><strong>Name:</strong> {customer_name}</p>
        <p><strong>Email:</strong> {submission_data.get('email', 'N/A')}</p>
        <p><strong>Phone:</strong> {submission_data.get('phoneNumber', 'N/A')}</p>
        <p><strong>Payment Method:</strong> {payment_details}</p>
        
        <h3 style="color: #374151; border-bottom: 2px solid #e5e7eb; padding-bottom: 5px;">Gift Card Details</h3>
        <div style="background: #f9fafb; padding: 15px; border-radius: 5px; white-space: pre-line;">
{cards_info}
        </div>
        
        <div style="background: #fef3c7; border: 1px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 5px;">
            <strong>Total Value:</strong> {total_value} dollars
        </div>
        
        <h3 style="color: #374151;">Next Steps:</h3>
        <p>1. Review customer and card information</p>
        <p>2. Verify gift card images (attached)</p>
        <p>3. Process payment within 24 hours</p>
        <p>4. Update customer with status</p>
        
        <hr style="margin: 30px 0;">
        <p style="font-size: 12px; color: #6b7280;">
            Submission Date: {submission_data.get('submitted_at', 'N/A')}<br>
            System: CashifyGCmart Internal Notification<br>
            From: noreply@cashifygcmart.com
        </p>
    </div>
</body>
</html>
"""
    cards_info = ""
    total_value = 0
    
    for i, card in enumerate(submission_data.get('cards', []), 1):
        card_value = float(card.get('value', 0)) if card.get('value', '').replace('.', '').isdigit() else 0
        total_value += card_value
        
        # Image status indicators
        front_img_status = "✅ Uploaded" if card.get('frontImage') else "❌ Missing"
        back_img_status = "✅ Uploaded" if card.get('backImage') else "❌ Missing"
        receipt_img_status = "✅ Uploaded" if card.get('receiptImage') else "❌ Not Required" if card.get('hasReceipt') == 'no' else "❌ Missing"
        digital_code = card.get('digitalCode', 'N/A') if card.get('cardType') == 'digital' else 'N/A'
        digital_pin = card.get('digitalPin', 'N/A') if card.get('cardType') == 'digital' else 'N/A'
        
        cards_info += f"""
        <tr style="border-bottom: 1px solid #e5e7eb;">
            <td style="padding: 12px; text-align: left; font-weight: bold;">{i}</td>
            <td style="padding: 12px; text-align: left;"><strong>{card.get('brand', 'N/A')}</strong></td>
            <td style="padding: 12px; text-align: left;"><strong>${card.get('value', '0')}</strong></td>
            <td style="padding: 12px; text-align: left;">{card.get('condition', 'N/A').replace('-', ' ').title()}</td>
            <td style="padding: 12px; text-align: left;">{"✅ Yes" if card.get('hasReceipt') == 'yes' else "❌ No"}</td>
            <td style="padding: 12px; text-align: left;">{card.get('cardType', 'N/A').title()}</td>
        </tr>
        <tr style="background-color: #f8fafc;">
            <td colspan="2" style="padding: 8px 12px; font-size: 12px;"><strong>Images:</strong></td>
            <td style="padding: 8px 12px; font-size: 12px;">Front: {front_img_status}</td>
            <td style="padding: 8px 12px; font-size: 12px;">Back: {back_img_status}</td>
            <td style="padding: 8px 12px; font-size: 12px;">Receipt: {receipt_img_status}</td>
            <td style="padding: 8px 12px; font-size: 12px;"></td>
        </tr>
        {"" if card.get('cardType') != 'digital' else f'''
        <tr style="background-color: #ecfef5;">
            <td colspan="3" style="padding: 8px 12px; font-size: 12px;"><strong>Digital Code:</strong> {digital_code}</td>
            <td colspan="3" style="padding: 8px 12px; font-size: 12px;"><strong>Digital PIN:</strong> {digital_pin}</td>
        </tr>
        '''}"""
    
    # Payment method details
    payment_details = ""
    payment_method = submission_data.get('paymentMethod', '').upper()
    if payment_method == 'PAYPAL':
        payment_details = f"PayPal Address: {submission_data.get('paypalAddress', 'Not provided')}"
    elif payment_method == 'ZELLE':
        payment_details = f"Zelle Details: {submission_data.get('zelleDetails', 'Not provided')}"
    elif payment_method == 'CASHAPP':
        payment_details = f"Cash App Tag: {submission_data.get('cashAppTag', 'Not provided')}"
    elif payment_method == 'BTC':
        payment_details = f"Bitcoin Address: {submission_data.get('btcAddress', 'Not provided')}"
    elif payment_method == 'CHIME':
        payment_details = f"Chime Details: {submission_data.get('chimeDetails', 'Not provided')}"
    
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Gift Card Submission - {reference_number}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .email-container {{
            max-width: 900px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
            color: white;
            padding: 25px 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .content {{
            padding: 25px;
        }}
        .reference-number {{
            background-color: #fee2e2;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #dc2626;
            text-align: center;
        }}
        .reference-number strong {{
            color: #dc2626;
            font-size: 18px;
        }}
        .section {{
            margin-bottom: 25px;
        }}
        .section-title {{
            color: #1e40af;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            background-color: #f0f9ff;
            padding: 8px 12px;
            border-radius: 6px;
        }}
        .customer-info {{
            background-color: #f8fafc;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }}
        .customer-info table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .customer-info td {{
            padding: 6px 12px;
            border-bottom: 1px solid #e5e7eb;
            font-size: 14px;
        }}
        .customer-info td:first-child {{
            font-weight: 600;
            width: 25%;
            color: #374151;
        }}
        .cards-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
            font-size: 13px;
        }}
        .cards-table th {{
            background-color: #1f2937;
            color: white;
            padding: 10px 8px;
            text-align: left;
            font-weight: 600;
            font-size: 12px;
        }}
        .urgent {{
            background-color: #fef2f2;
            border: 2px solid #fca5a5;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }}
        .urgent strong {{
            color: #dc2626;
        }}
        .total-value {{
            background-color: #ecfdf5;
            border: 2px solid #a3e635;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            margin: 15px 0;
        }}
        .total-value strong {{
            color: #166534;
            font-size: 18px;
        }}
        .actions {{
            background-color: #fffbeb;
            border: 1px solid #fbbf24;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }}
        .footer {{
            background-color: #f9fafb;
            padding: 15px;
            text-align: center;
            color: #6b7280;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>🚨 NEW GIFT CARD SUBMISSION RECEIVED</h1>
        </div>
        
        <div class="content">
            <div class="reference-number">
                <strong>Reference Number: {reference_number}</strong><br>
                <span style="font-size: 12px; color: #6b7280;">Submitted: {submission_data.get('submitted_at', 'Just Now')}</span>
            </div>
            
            <div class="urgent">
                <strong>⏰ IMMEDIATE ACTION REQUIRED:</strong> New submission requires verification and response within 14 hours per customer promise.
            </div>
            
            <div class="section">
                <h2 class="section-title">👤 CUSTOMER INFORMATION</h2>
                <div class="customer-info">
                    <table>
                        <tr>
                            <td><strong>Full Name:</strong></td>
                            <td><strong>{customer_name}</strong></td>
                        </tr>
                        <tr>
                            <td><strong>Email Address:</strong></td>
                            <td><a href="mailto:{submission_data.get('email')}" style="color: #3b82f6;">{submission_data.get('email')}</a></td>
                        </tr>
                        <tr>
                            <td><strong>Phone Number:</strong></td>
                            <td>{submission_data.get('phoneNumber', 'Not provided')}</td>
                        </tr>
                        <tr>
                            <td><strong>Payment Method:</strong></td>
                            <td><strong>{payment_method}</strong></td>
                        </tr>
                        <tr>
                            <td><strong>Payment Details:</strong></td>
                            <td>{payment_details}</td>
                        </tr>
                    </table>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">💳 GIFT CARD SUBMISSION DETAILS</h2>
                <table class="cards-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Brand</th>
                            <th>Value</th>
                            <th>Condition</th>
                            <th>Receipt</th>
                            <th>Type</th>
                        </tr>
                    </thead>
                    <tbody>
                        {cards_info}
                    </tbody>
                </table>
            </div>
            
            <div class="total-value">
                <strong>💰 TOTAL SUBMISSION VALUE: ${total_value:.2f}</strong>
            </div>
            
            <div class="actions">
                <h3 style="margin: 0 0 10px 0; color: #92400e;">📋 REQUIRED ACTIONS:</h3>
                <ol style="margin: 0; padding-left: 20px; color: #92400e;">
                    <li><strong>Verify Images:</strong> Check all uploaded card images and receipts</li>
                    <li><strong>Validate Details:</strong> Confirm card brands, values, and conditions</li>
                    <li><strong>Process Payment Info:</strong> Verify {payment_method} details</li>
                    <li><strong>Calculate Rates:</strong> Apply current rates for approval/offer</li>
                    <li><strong>Respond to Customer:</strong> Email {submission_data.get('email')} within 14 hours</li>
                </ol>
            </div>
            
            <div style="background-color: #f0fdf4; padding: 12px; border-radius: 8px; text-align: center; font-size: 13px; color: #166534;">
                <strong>Customer Reference Number: {reference_number}</strong><br>
                Customer confirmation email automatically sent to: {submission_data.get('email')}
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background-color: #fee2e2; border-radius: 8px; border-left: 4px solid #dc2626;">
                <strong style="color: #dc2626;">⚠️ IMPORTANT:</strong> All uploaded images are attached to this email. Customer has been instructed not to use the gift card during review period.
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Cashifygcmart Operations Alert</strong></p>
            <p>This is an automated notification. Customer awaiting response within 14 hours.</p>
            <p>Forward to: marketingmanager3059@gmail.com</p>
        </div>
    </div>
</body>
</html>
    """

# Resend email sending function for internal notifications with attachments
async def send_internal_notification_email(submission_data: dict, customer_name: str, reference_number: str):
    try:
        # Get SMTP settings from environment
        smtp_server = os.environ.get('SMTP_SERVER')
        smtp_port = int(os.environ.get('SMTP_PORT', 465))
        smtp_username = os.environ.get('SMTP_USERNAME')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        use_ssl = os.environ.get('SMTP_USE_SSL', 'true').lower() == 'true'
        operations_email = os.environ.get('OPERATIONS_EMAIL')
        
        if not all([smtp_server, smtp_username, smtp_password, operations_email]):
            print("ERROR: SMTP settings or operations email not found in environment variables")
            return False
        
        # Calculate total value for subject line
        total_value = sum([float(card.get('value', 0)) if card.get('value', '').replace('.', '').isdigit() else 0 
                          for card in submission_data.get('cards', [])])
        
        # Generate email content
        email_html = generate_internal_notification_email(customer_name, reference_number, submission_data)
        subject = f"New Form Submission - Reference {reference_number} - {customer_name}"
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = operations_email
        msg['Subject'] = subject
        
        # Add HTML content
        html_part = MIMEText(email_html, 'html')
        msg.attach(html_part)
        
        # Process file attachments from uploaded images
        attachment_count = 0
        for i, card in enumerate(submission_data.get('cards', []), 1):
            # Handle front image
            if card.get('frontImage') and isinstance(card['frontImage'], dict):
                if 'data' in card['frontImage'] and 'name' in card['frontImage']:
                    try:
                        # Decode base64 image data
                        import base64
                        image_data = card['frontImage']['data']
                        if image_data.startswith('data:'):
                            # Remove data URL prefix
                            image_data = image_data.split(',')[1]
                        
                        # Decode base64
                        decoded_data = base64.b64decode(image_data)
                        
                        # Create attachment
                        attachment = MIMEBase('application', 'octet-stream')
                        attachment.set_payload(decoded_data)
                        encoders.encode_base64(attachment)
                        attachment.add_header(
                            'Content-Disposition',
                            f'attachment; filename=Card_{i}_Front_{card["frontImage"]["name"]}'
                        )
                        msg.attach(attachment)
                        attachment_count += 1
                    except Exception as e:
                        print(f"Failed to attach front image for card {i}: {e}")
            
            # Handle back image
            if card.get('backImage') and isinstance(card['backImage'], dict):
                if 'data' in card['backImage'] and 'name' in card['backImage']:
                    try:
                        import base64
                        image_data = card['backImage']['data']
                        if image_data.startswith('data:'):
                            image_data = image_data.split(',')[1]
                        
                        decoded_data = base64.b64decode(image_data)
                        
                        attachment = MIMEBase('application', 'octet-stream')
                        attachment.set_payload(decoded_data)
                        encoders.encode_base64(attachment)
                        attachment.add_header(
                            'Content-Disposition',
                            f'attachment; filename=Card_{i}_Back_{card["backImage"]["name"]}'
                        )
                        msg.attach(attachment)
                        attachment_count += 1
                    except Exception as e:
                        print(f"Failed to attach back image for card {i}: {e}")
            
            # Handle receipt image
            if card.get('receiptImage') and isinstance(card['receiptImage'], dict):
                if 'data' in card['receiptImage'] and 'name' in card['receiptImage']:
                    try:
                        import base64
                        image_data = card['receiptImage']['data']
                        if image_data.startswith('data:'):
                            image_data = image_data.split(',')[1]
                        
                        decoded_data = base64.b64decode(image_data)
                        
                        attachment = MIMEBase('application', 'octet-stream')
                        attachment.set_payload(decoded_data)
                        encoders.encode_base64(attachment)
                        attachment.add_header(
                            'Content-Disposition',
                            f'attachment; filename=Card_{i}_Receipt_{card["receiptImage"]["name"]}'
                        )
                        msg.attach(attachment)
                        attachment_count += 1
                    except Exception as e:
                        print(f"Failed to attach receipt image for card {i}: {e}")
        
        # Send email via SMTP
        if use_ssl:
            # SSL connection
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
        else:
            # TLS connection
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
        
        print(f"✅ Internal notification email sent to: {operations_email}")
        print(f"📎 Attachments included: {attachment_count}")
        print(f"Reference Number: {reference_number}")
        return True
        
    except Exception as e:
        print(f"❌ SMTP internal email sending failed: {e}")
        return False

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check():
    status_obj = StatusCheck()
    if db:
        _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.post("/submit-gift-card")
async def submit_gift_card(submission: GiftCardSubmission):
    try:
        # Generate unique reference number
        reference_number = generate_reference_number()
        
        # Add metadata to submission
        submission_data = submission.dict()
        submission_data["reference_number"] = reference_number
        submission_data["status"] = "under_review"
        submission_data["submitted_at"] = datetime.now().isoformat()
        
        # Save to database
        if db:
            await db.gift_card_submissions.insert_one(submission_data)
        
        # Send emails
        customer_name = f"{submission.firstName} {submission.lastName}"
        
        # 1. Send customer confirmation email
        customer_email_sent = await send_confirmation_email(
            submission.email, 
            customer_name, 
            reference_number
        )
        
        # 2. Send internal notification email to operations team
        internal_email_sent = await send_internal_notification_email(
            submission_data,
            customer_name, 
            reference_number
        )
        
        return {
            "success": True,
            "reference_number": reference_number,
            "message": "Gift card submission received successfully",
            "customer_email_sent": customer_email_sent,
            "internal_email_sent": internal_email_sent
        }
        
    except Exception as e:
        logging.error(f"Gift card submission error: {e}")
        return {
            "success": False,
            "message": "An error occurred while processing your submission"
        }

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    if db:
        status_checks = await db.status_checks.find().to_list(1000)
        return [StatusCheck(**status_check) for status_check in status_checks]
    else:
        return [StatusCheck(message="Demo mode - no database")]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()
