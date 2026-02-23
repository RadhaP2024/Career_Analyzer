from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend - MUST come before pyplot import
import matplotlib.pyplot as plt
import numpy as np
import os
from django.conf import settings
from .models import EngineeringBranch, Company, Course, Project, UserFeedback

# Helper function to generate placement chart
def generate_placement_chart():
    branches = EngineeringBranch.objects.all()
    if not branches:
        return None

    names = [b.name for b in branches]
    placement_2024 = [b.placement_2024 for b in branches]
    placement_2026 = [b.placement_2026 for b in branches]

    x = np.arange(len(names))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars1 = ax.bar(x - width/2, placement_2024, width, label='2024', color='#3498db')
    bars2 = ax.bar(x + width/2, placement_2026, width, label='2026', color='#e74c3c')
    
    ax.set_xlabel('Engineering Branches')
    ax.set_ylabel('Placement Percentage (%)')
    ax.set_title('Placement Rates: 2024 vs 2026')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha='right')
    ax.legend()
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    
    # Create media directory if it doesn't exist
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    
    # Save chart
    chart_path = os.path.join(settings.MEDIA_ROOT, 'placement_chart.png')
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    return 'placement_chart.png'

# Helper function to generate salary chart
def generate_salary_chart():
    branches = EngineeringBranch.objects.all()
    if not branches:
        return None

    names = [b.name for b in branches]
    salaries = [b.salary_2024 for b in branches]
    
    colors = ['#2ecc71', '#3498db', '#9b59b6', '#e67e22', '#1abc9c', '#e74c3c']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(names, salaries, color=colors[:len(names)])
    
    ax.set_xlabel('Engineering Branches')
    ax.set_ylabel('Salary (Lakhs per Annum)')
    ax.set_title('Average Salary Package 2024')
    ax.set_xticklabels(names, rotation=45, ha='right')
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'₹{height}L',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    
    # Create media directory if it doesn't exist
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    
    # Save chart
    chart_path = os.path.join(settings.MEDIA_ROOT, 'salary_chart.png')
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    return 'salary_chart.png'

# Helper function to generate growth chart
def generate_growth_chart():
    branches = EngineeringBranch.objects.all()
    if not branches:
        return None

    names = [b.name for b in branches]
    growth = [b.placement_growth() for b in branches]
    
    colors = ['#27ae60' if g > 0 else '#c0392b' for g in growth]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(names, growth, color=colors)
    
    ax.set_xlabel('Engineering Branches')
    ax.set_ylabel('Growth (%)')
    ax.set_title('Placement Growth: 2024 to 2026')
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax.set_xticklabels(names, rotation=45, ha='right')
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:+.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5 if height > 0 else -15),
                    textcoords="offset points",
                    ha='center', va='bottom' if height > 0 else 'top',
                    fontsize=10)
    
    plt.tight_layout()
    
    # Create media directory if it doesn't exist
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    
    # Save chart
    chart_path = os.path.join(settings.MEDIA_ROOT, 'growth_chart.png')
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    return 'growth_chart.png'

# Home page
def index(request):
    branches = EngineeringBranch.objects.all()
    context = {
        'branches': branches,
        'total_branches': branches.count(),
    }
    return render(request, 'analyzer/index.html', context)

# All branches
def all_branches(request):
    branches = EngineeringBranch.objects.all()
    return render(request, 'analyzer/all_branches.html', {'branches': branches})

# Placement comparison
def placement_comparison(request):
    branches = EngineeringBranch.objects.all()
    
    # Generate chart
    chart_file = generate_placement_chart()
    
    # Calculate growth
    for branch in branches:
        branch.growth = branch.placement_growth()
        branch.growth_icon = "📈" if branch.growth > 0 else "📉"
    
    context = {
        'branches': branches,
        'chart_file': chart_file,
    }
    return render(request, 'analyzer/placement_comparison.html', context)

# Salary analysis
def salary_analysis(request):
    branches = EngineeringBranch.objects.all()
    
    # Generate chart
    chart_file = generate_salary_chart()
    growth_chart = generate_growth_chart()
    
    max_salary = max([b.salary_2024 for b in branches]) if branches else 1
    
    for branch in branches:
        branch.bar_length = int((branch.salary_2024 / max_salary) * 20)
        branch.bar = '█' * branch.bar_length
    
    context = {
        'branches': branches,
        'chart_file': chart_file,
        'growth_chart': growth_chart,
        'max_salary': max_salary,
    }
    return render(request, 'analyzer/salary_analysis.html', context)

def market_analysis(request):
    branches = EngineeringBranch.objects.all()
    print(f"===== DEBUG: Found {branches.count()} branches =====")  # This shows in terminal
    for branch in branches:
        print(f"  - {branch.name}: {branch.placement_2024}%")
    context = {
        'branches': branches,
    }
    return render(request, 'analyzer/market_analysis.html', context)

# Branch details
def branch_detail(request, branch_id):
    branch = get_object_or_404(EngineeringBranch, id=branch_id)
    companies = Company.objects.filter(branch=branch)
    courses = Course.objects.filter(branch=branch)[:5]
    projects = Project.objects.filter(branch=branch)[:5]
    
    if branch.placement_2024 >= 80:
        verdict = "Excellent choice! High demand field! 🎯"
    elif branch.placement_2024 >= 70:
        verdict = "Good choice with growing opportunities! 👍"
    else:
        verdict = "Stable field with niche opportunities! 🔧"
    
    context = {
        'branch': branch,
        'companies': companies,
        'courses': courses,
        'projects': projects,
        'verdict': verdict,
    }
    return render(request, 'analyzer/branch_detail.html', context)

# Compare branches
def compare_branches(request):
    branches = EngineeringBranch.objects.all()
    branch1 = None
    branch2 = None
    score1 = 0
    score2 = 0
    
    if request.method == 'POST':
        branch1_id = request.POST.get('branch1')
        branch2_id = request.POST.get('branch2')
        
        if branch1_id and branch2_id and branch1_id != branch2_id:
            branch1 = get_object_or_404(EngineeringBranch, id=branch1_id)
            branch2 = get_object_or_404(EngineeringBranch, id=branch2_id)
            score1 = branch1.placement_2024 + (branch1.salary_2024 * 8)
            score2 = branch2.placement_2024 + (branch2.salary_2024 * 8)
    
    context = {
        'branches': branches,
        'branch1': branch1,
        'branch2': branch2,
        'score1': score1,
        'score2': score2,
    }
    return render(request, 'analyzer/branch_compare.html', context)

# Career suggestion
def career_suggestion(request):
    suggested_branch = None
    
    if request.method == 'POST':
        interest = request.POST.get('interest')
        interest_map = {
            '1': 'Computer Science',
            '2': 'Mechanical',
            '3': 'Civil',
            '4': 'Electronics',
            '5': 'Chemical',
            '6': 'Aerospace'
        }
        if interest in interest_map:
            suggested_branch = EngineeringBranch.objects.filter(name=interest_map[interest]).first()
    
    return render(request, 'analyzer/career_suggestion.html', {'suggested_branch': suggested_branch})

# Market analysis
def market_analysis(request):
    branches = EngineeringBranch.objects.all()
    best_placement = max(branches, key=lambda x: x.placement_2024) if branches else None
    highest_salary = max(branches, key=lambda x: x.salary_2024) if branches else None
    growth_branches = sorted(branches, key=lambda x: x.placement_growth(), reverse=True)[:3] if branches else []
    
    context = {
        'best_placement': best_placement,
        'highest_salary': highest_salary,
        'growth_branches': growth_branches,
    }
    return render(request, 'analyzer/market_analysis.html', context)

# Chatbot - Main page
def chatbot(request):
    return render(request, 'analyzer/chatbot.html')

# Chatbot API - handles AJAX requests
def chatbot_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_input = data.get('message', '').lower().strip()
        
        response = generate_chatbot_response(user_input)
        
        # Save feedback
        UserFeedback.objects.create(
            user_input=user_input,
            bot_response=response
        )
        
        return JsonResponse({'response': response})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def generate_chatbot_response(user_input):
    """Generate chatbot response based on user input"""
    
    # Get all branches for data
    branches = EngineeringBranch.objects.all()
    
    # Greetings
    if any(word in user_input for word in ['hi', 'hello', 'hey', 'greetings']):
        return "👋 Hello! I'm your Engineering Career Assistant. Ask me about placements, salaries, courses, or specific branches!"
    
    # Help
    if 'help' in user_input:
        return """🤖 **I can help you with:**
• Placement rates - Ask "placement rates" or "placements"
• Salary information - Ask "salaries" or "salary packages"
• Branch details - Ask "about Computer Science" or "tell me about Mechanical"
• Course recommendations - Ask "courses for Electronics" or "NPTEL courses"
• Project ideas - Ask "projects for Civil" or "project ideas"
• Comparisons - Ask "compare CS and Mechanical"
• Future trends - Ask "future trends" or "growing fields"
• Career suggestions - Ask "suggest career" or "what should I choose"

Just type your question! 🎯"""
    
    # Placement rates
    if 'placement' in user_input:
        response = "📊 **Placement Rates 2024:**\n\n"
        for branch in branches:
            response += f"• {branch.name}: {branch.placement_2024}%\n"
        response += "\n📈 **Fastest Growing:**\n"
        top_growth = sorted(branches, key=lambda x: x.placement_growth(), reverse=True)[:2]
        for branch in top_growth:
            response += f"• {branch.name}: +{branch.placement_growth()}% growth\n"
        return response
    
    # Salary information
    if 'salary' in user_input or 'package' in user_input:
        response = "💰 **Average Salary Packages 2024:**\n\n"
        for branch in branches:
            response += f"• {branch.name}: ₹{branch.salary_2024} LPA\n"
        highest = max(branches, key=lambda x: x.salary_2024)
        response += f"\n🏆 **Highest:** {highest.name} with ₹{highest.salary_2024} LPA"
        return response
    
    # Future trends
    if 'future' in user_input or 'trend' in user_input or 'growing' in user_input:
        response = "🔮 **Future Trends & Growing Fields:**\n\n"
        for branch in branches:
            response += f"• **{branch.name}:** {branch.future_trends}\n"
        return response
    
    # Skills
    if 'skill' in user_input:
        response = "🔧 **In-Demand Skills for 2026:**\n\n"
        for branch in branches:
            response += f"• **{branch.name}:** {branch.future_skills}\n"
        return response
    
    # Courses
    if 'course' in user_input:
        # Extract branch if mentioned
        for branch in branches:
            if branch.name.lower() in user_input:
                courses = Course.objects.filter(branch=branch)[:4]
                if courses:
                    response = f"🎓 **Recommended Courses for {branch.name}:**\n\n"
                    for course in courses:
                        free_icon = "🆓" if course.is_free else "💰"
                        response += f"• **{course.name}**\n  {free_icon} {course.platform} | {course.level} | {course.duration}\n"
                    return response
                else:
                    return f"No courses found for {branch.name} yet."
        
        # If no specific branch, show popular courses
        response = "🎓 **Popular Courses:**\n\n"
        popular_courses = Course.objects.all()[:5]
        for course in popular_courses:
            response += f"• **{course.name}** ({course.platform}) - {course.branch.name}\n"
        return response
    
    # Projects
    if 'project' in user_input:
        # Extract branch if mentioned
        for branch in branches:
            if branch.name.lower() in user_input:
                projects = Project.objects.filter(branch=branch)[:4]
                if projects:
                    response = f"🔧 **Project Ideas for {branch.name}:**\n\n"
                    for project in projects:
                        response += f"• {project.name} ({project.difficulty})\n"
                    return response
                else:
                    return f"No projects found for {branch.name} yet."
        
        # If no specific branch, show all projects
        response = "🔧 **Project Ideas by Branch:**\n\n"
        for branch in branches[:3]:
            projects = Project.objects.filter(branch=branch)[:2]
            if projects:
                response += f"**{branch.name}:**\n"
                for project in projects:
                    response += f"  • {project.name}\n"
                response += "\n"
        return response
    
    # Branch information
    for branch in branches:
        if branch.name.lower() in user_input or branch.code.lower() in user_input:
            return f"""📚 **{branch.name} Engineering {branch.icon}**

**Placement 2024:** {branch.placement_2024}%
**Placement 2026:** {branch.placement_2026}% ({branch.placement_growth():+.1f}% growth)
**Salary:** ₹{branch.salary_2024} LPA

**Future Trend:** {branch.future_trends}

**Key Skills:** {branch.future_skills}

Ask me about courses or projects for {branch.name}!"""
    
    # Compare branches
    if 'compare' in user_input:
        words = user_input.split()
        branch_names = []
        for word in words:
            for branch in branches:
                if branch.name.lower() in word.lower() or branch.code.lower() in word.lower():
                    branch_names.append(branch.name)
        
        if len(branch_names) >= 2:
            b1 = EngineeringBranch.objects.get(name=branch_names[0])
            b2 = EngineeringBranch.objects.get(name=branch_names[1])
            return f"""🔄 **Comparison: {b1.name} vs {b2.name}**

**Placement 2024:** {b1.placement_2024}% vs {b2.placement_2024}%
**Salary:** ₹{b1.salary_2024}L vs ₹{b2.salary_2024}L
**Growth:** +{b1.placement_growth()}% vs +{b2.placement_growth()}%

**Winner:** {b1.name if b1.placement_2024 + b1.salary_2024*8 > b2.placement_2024 + b2.salary_2024*8 else b2.name}"""
    
    # Default response
    return """I'm not sure I understand. Try asking about:
• Placement rates
• Salary packages
• Specific branches (like "Computer Science")
• Courses or projects
• Future trends

Type 'help' for more options! 🤖"""

# Courses page
def courses(request):
    branches = EngineeringBranch.objects.all()
    courses = Course.objects.all()
    branch_filter = request.GET.get('branch', '')
    platform_filter = request.GET.get('platform', '')
    
    if branch_filter:
        courses = courses.filter(branch__name=branch_filter)
    if platform_filter:
        courses = courses.filter(platform=platform_filter)
    
    context = {
        'branches': branches,
        'courses': courses,
        'branch_filter': branch_filter,
        'platform_filter': platform_filter,
    }
    return render(request, 'analyzer/courses.html', context)

# Projects page
def projects(request):
    branches = EngineeringBranch.objects.all()
    projects = Project.objects.all()
    branch_filter = request.GET.get('branch', '')
    
    if branch_filter:
        projects = projects.filter(branch__name=branch_filter)
    
    context = {
        'branches': branches,
        'projects': projects,
        'branch_filter': branch_filter,
    }
    return render(request, 'analyzer/projects.html', context)

# About page
def about(request):
    return render(request, 'analyzer/about.html')

# Load initial data
def load_initial_data(request):
    # Clear existing data
    EngineeringBranch.objects.all().delete()
    Company.objects.all().delete()
    Course.objects.all().delete()
    Project.objects.all().delete()
    
    # Create branches
    branches_data = [
        {"name": "Computer Science", "code": "CS", "placement_2024": 88, "placement_2026": 91, "salary_2024": 9.2,
         "future_trends": "AI jobs will grow by 40%, Cybersecurity demand increasing, Cloud computing expansion",
         "future_skills": "AI/ML, Cloud Computing, Cybersecurity, Data Science, Full Stack Development", "icon": "💻"},
        {"name": "Mechanical", "code": "ME", "placement_2024": 72, "placement_2026": 75, "salary_2024": 6.5,
         "future_trends": "EV sector boom, Robotics automation expanding, Additive manufacturing growth",
         "future_skills": "CAD/CAM, Robotics, EV Technology, 3D Printing, Thermodynamics", "icon": "🚗"},
        {"name": "Civil", "code": "CE", "placement_2024": 68, "placement_2026": 70, "salary_2024": 5.9,
         "future_trends": "Infrastructure projects under National Pipeline, Smart cities, Green building",
         "future_skills": "BIM, Project Management, Sustainable Materials, Structural Analysis", "icon": "🏗️"},
        {"name": "Electronics", "code": "EC", "placement_2024": 79, "placement_2026": 82, "salary_2024": 7.8,
         "future_trends": "Semiconductor industry growth, IoT devices expansion, 5G implementation",
         "future_skills": "VLSI, Embedded Systems, IoT, PCB Design, Communication Systems", "icon": "📱"},
        {"name": "Chemical", "code": "CH", "placement_2024": 71, "placement_2026": 74, "salary_2024": 6.8,
         "future_trends": "Green chemistry emerging, Pharmaceutical sector stable, Sustainable processes",
         "future_skills": "Process Optimization, Green Chemistry, Data Analysis, Thermodynamics", "icon": "⚗️"},
        {"name": "Aerospace", "code": "AE", "placement_2024": 75, "placement_2026": 78, "salary_2024": 8.1,
         "future_trends": "Space tech growing, Drone technology expanding, Commercial space flight",
         "future_skills": "Aerodynamics, Composite Materials, Drone Tech, Propulsion Systems", "icon": "✈️"},
    ]
    
    branches = []
    for data in branches_data:
        branch = EngineeringBranch.objects.create(**data)
        branches.append(branch)
    
    # Companies
    companies_data = {
        "Computer Science": ["Google", "Microsoft", "Amazon", "Infosys", "TCS", "Wipro", "Facebook", "Apple"],
        "Mechanical": ["TATA Motors", "Mahindra", "L&T", "Maruti Suzuki", "John Deere", "BHEL", "Siemens"],
        "Civil": ["L&T Construction", "Shapoorji Pallonji", "TATA Projects", "GMR Group", "DLF", "Prestige"],
        "Electronics": ["Intel", "Samsung", "Qualcomm", "Texas Instruments", "NVIDIA", "AMD", "Broadcom"],
        "Chemical": ["Reliance", "BASF", "Dow Chemical", "Shell", "BPCL", "IOCL", "ONGC"],
        "Aerospace": ["ISRO", "DRDO", "Boeing", "Airbus", "HAL", "SpaceX", "Blue Origin"],
    }
    
    for branch in branches:
        for company_name in companies_data[branch.name]:
            Company.objects.create(name=company_name, branch=branch)
    
    # Courses
    courses_data = {
        "Computer Science": [
            {"platform": "NPTEL", "name": "Programming in Java", "level": "Intermediate", "duration": "12 weeks", "is_free": True},
            {"platform": "Coursera", "name": "Machine Learning by Andrew Ng", "level": "Beginner", "duration": "11 weeks", "is_free": False},
            {"platform": "edX", "name": "CS50's Introduction to CS", "level": "Beginner", "duration": "12 weeks", "is_free": True},
            {"platform": "Udemy", "name": "Web Development Bootcamp", "level": "Beginner", "duration": "55 hours", "is_free": False},
            {"platform": "NPTEL", "name": "Data Structures and Algorithms", "level": "Intermediate", "duration": "8 weeks", "is_free": True},
        ],
        "Mechanical": [
            {"platform": "NPTEL", "name": "Introduction to Electric Vehicles", "level": "Beginner", "duration": "8 weeks", "is_free": True},
            {"platform": "Coursera", "name": "Robotics Specialization", "level": "Intermediate", "duration": "7 months", "is_free": False},
            {"platform": "edX", "name": "CAD and Digital Manufacturing", "level": "Intermediate", "duration": "9 weeks", "is_free": True},
            {"platform": "NPTEL", "name": "Automobile Engineering", "level": "Advanced", "duration": "12 weeks", "is_free": True},
        ],
        "Civil": [
            {"platform": "NPTEL", "name": "Building Information Modeling", "level": "Intermediate", "duration": "8 weeks", "is_free": True},
            {"platform": "Coursera", "name": "Construction Management", "level": "Beginner", "duration": "6 months", "is_free": False},
            {"platform": "edX", "name": "Sustainable Building Design", "level": "Intermediate", "duration": "10 weeks", "is_free": True},
        ],
        "Electronics": [
            {"platform": "NPTEL", "name": "VLSI Design", "level": "Advanced", "duration": "12 weeks", "is_free": True},
            {"platform": "Coursera", "name": "IoT Programming", "level": "Intermediate", "duration": "7 weeks", "is_free": False},
            {"platform": "edX", "name": "Embedded Systems", "level": "Beginner", "duration": "8 weeks", "is_free": True},
        ],
        "Chemical": [
            {"platform": "NPTEL", "name": "Process Integration", "level": "Advanced", "duration": "8 weeks", "is_free": True},
            {"platform": "Coursera", "name": "Introduction to Chemistry", "level": "Beginner", "duration": "7 weeks", "is_free": True},
            {"platform": "edX", "name": "Sustainable Chemical Engineering", "level": "Intermediate", "duration": "6 weeks", "is_free": True},
        ],
        "Aerospace": [
            {"platform": "NPTEL", "name": "Aerodynamics", "level": "Advanced", "duration": "12 weeks", "is_free": True},
            {"platform": "Coursera", "name": "Flight Mechanics", "level": "Intermediate", "duration": "8 weeks", "is_free": False},
            {"platform": "edX", "name": "Introduction to Aeronautical Engineering", "level": "Beginner", "duration": "7 weeks", "is_free": True},
        ],
    }
    
    for branch in branches:
        if branch.name in courses_data:
            for course_data in courses_data[branch.name]:
                Course.objects.create(branch=branch, **course_data)
    
    # Projects
    projects_data = {
        "Computer Science": [
            "AI Chatbot using Python and NLP",
            "E-commerce Website with React",
            "Mobile App with Flutter",
            "Stock Price Prediction Model",
            "Blockchain-based Voting System",
            "Cybersecurity Threat Detection"
        ],
        "Mechanical": [
            "Electric Vehicle Conversion Kit",
            "3D Printed Prosthetic Hand",
            "Automated Solar Panel Cleaner",
            "RC Aircraft with FPV System",
            "Hydraulic Robotic Arm",
            "Smart Irrigation System"
        ],
        "Civil": [
            "BIM Model for Smart Building",
            "Earthquake Resistant Design",
            "Green Building with Sustainable Materials",
            "Traffic Management System",
            "Bridge Health Monitoring",
            "Water Treatment Plant Design"
        ],
        "Electronics": [
            "IoT Home Automation System",
            "Arduino Weather Station",
            "PCB Design for Power Supply",
            "Drone with GPS Navigation",
            "Digital Oscilloscope",
            "Smart Energy Meter"
        ],
        "Chemical": [
            "Biodiesel Production from Waste Oil",
            "Water Purification System",
            "Plastic Recycling Process",
            "Chemical Process Simulation",
            "Nanomaterial Synthesis",
            "Food Preservation Technology"
        ],
        "Aerospace": [
            "Quadcopter with Autonomous Navigation",
            "Rocket Propulsion System Design",
            "Aircraft Wing Design Optimization",
            "Satellite Communication System",
            "Drone-based Delivery System",
            "Aerodynamic Analysis"
        ],
    }
    
    for branch in branches:
        if branch.name in projects_data:
            for project_name in projects_data[branch.name]:
                difficulty = "Medium"
                if "AI" in project_name or "Rocket" in project_name:
                    difficulty = "Hard"
                elif "Weather" in project_name or "Website" in project_name:
                    difficulty = "Easy"
                Project.objects.create(name=project_name, branch=branch, difficulty=difficulty)
    
    messages.success(request, '✅ Initial data loaded successfully!')
    return index(request)