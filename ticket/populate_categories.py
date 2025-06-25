from ticket.models import Category

categories = {
    "Academic Related Support": ["Academics", "AIDS", "AIML", "CCE", "CSBS", "CSE", "ECE", "Innovation", "IQAC", "Maths", "Mech", "Research", "Science and Humanities"],
    "Events Related Admin Support": ["1st Floor Auditorium", "2nd Floor Auditorium", "Food & Refreshment", "GF 07", "Gift & Mementos", "Guest House Booking", "IOT Lab", "IT Center Venue", "Main Board Room", "Multipurpose Hall - Mech Block", "Seminar Hall Booking", "Transport Support"],
    "Facilities & Maintenance Support": ["Carpentry Work Related Issues", "Electrical & Plumbing", "Facility Repairs Related - Civil", "Glass Related Issues", "Others"],
    "General Admin Support": ["Food Related Queries", "Others", "Stationary", "Transport Related Queries"],
    "HR: General Employee Support": ["Employee Issues/Clarifications", "Policies", "Portal Issues"],
    "HR: Leave & Attendance Support": ["Leave & Attendance Policy Related", "Leave Queries", "Other", "Time & Attendance"],
    "HR: Letters Related Support": ["Address Proof Letter", "Bonafide Letter/No Objection Certificate", "Joining Letter", "Other", "Promotion Letter"],
    "IT & Networks: Hardware Support": ["Hardware Issues", "Keyboard & Mouse Issues", "Monitor Issues", "Others", "Request for Printers/Toners", "Request for System", "Request for Toner Replacement"],
    "IT & Networks: Software Support": ["Attendance Device Alert - Keka Sync Tool Alert - Lost Connection to Device", "Internet Issues", "Login Issues", "Other", "Request for CCTV Footage", "System Setup"],
    "Media": ["Acrylic Board - COE", "Admission Form", "Advertisement Posters", "Banners", "Bill Books", "Booklets", "Brochures", "Business Card", "Certificates", "Classroom Quotes", "College Diary - Front Page", "College Notebooks", "Cover Page", "Faculty Name Board", "Flex Design", "Flyer", "Foam Boards", "Invitation", "IR Dept Posters", "Lab Manuals", "Light Settings", "Momento Samples", "Newsletter", "Photos", "Photos & Videos", "Posters", "PowerPoint Presentation", "Pre-event Poster", "QR Scan - Video", "Sign Boards", "Standies", "Stickers", "TV Display Poster", "Video Edit", "Video Shoot", "Vinyl Board", "Website Banner", "Website Photo Edit", "Wrapper"],
    "Payroll: Bank Account & Insurance Support": ["Bank Account", "ESI", "Insurance", "Other", "PF Deductions", "UAN Details"],
    "Payroll: General Support": ["Bonus & Incentives", "Loans", "Other", "Payslips & Deductions", "Salary & Earnings"],
    "Payroll: Tax Support": ["Form 16", "Income Tax Deductions", "Investments", "Other", "Proof Submissions"],
    "PMS - 2024 to 2025 - HR": ["Additional Responsibilities", "Goal Removal", "Weightage"],
}

def populate_categories():
    for parent_name, subcategories in categories.items():
        # Create or get the parent category
        parent_category, created = Category.objects.get_or_create(name=parent_name)
        
        # Create subcategories and assign the parent_name
        for subcategory_name in subcategories:
            Category.objects.get_or_create(name=subcategory_name, parent_name=parent_name)

# Call the function to populate the categories
populate_categories()