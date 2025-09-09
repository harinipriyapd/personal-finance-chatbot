import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserProfile:
    """User profile to store demographic and financial information"""
    user_type: str  # 'student' or 'professional'
    age: int
    income: Optional[float] = None
    expenses: Dict[str, float] = None
    financial_goals: List[str] = None
    risk_tolerance: str = 'moderate'  # 'low', 'moderate', 'high'
    
    def __post_init__(self):
        if self.expenses is None:
            self.expenses = {}
        if self.financial_goals is None:
            self.financial_goals = []

class FinancialAnalyzer:
    """Core financial analysis and recommendation engine"""
    
    def __init__(self):
        self.tax_brackets_2024 = {
            'single': [
                (0, 11000, 0.10),
                (11000, 44725, 0.12),
                (44725, 95375, 0.22),
                (95375, 182050, 0.24),
                (182050, 231250, 0.32),
                (231250, 578125, 0.35),
                (578125, float('inf'), 0.37)
            ]
        }
    
    def calculate_tax_estimate(self, income: float, filing_status: str = 'single') -> Dict:
        """Calculate estimated federal taxes"""
        brackets = self.tax_brackets_2024.get(filing_status, self.tax_brackets_2024['single'])
        total_tax = 0
        tax_breakdown = []
        
        for i, (lower, upper, rate) in enumerate(brackets):
            if income <= lower:
                break
            
            taxable_in_bracket = min(income, upper) - lower
            tax_in_bracket = taxable_in_bracket * rate
            total_tax += tax_in_bracket
            
            if taxable_in_bracket > 0:
                tax_breakdown.append({
                    'bracket': f"{rate*100}%",
                    'range': f"${lower:,.0f} - ${upper:,.0f}" if upper != float('inf') else f"${lower:,.0f}+",
                    'taxable_amount': taxable_in_bracket,
                    'tax_amount': tax_in_bracket
                })
        
        return {
            'total_tax': total_tax,
            'effective_rate': (total_tax / income) * 100 if income > 0 else 0,
            'after_tax_income': income - total_tax,
            'breakdown': tax_breakdown
        }
    
    def analyze_budget(self, income: float, expenses: Dict[str, float]) -> Dict:
        """Analyze budget and provide insights"""
        total_expenses = sum(expenses.values())
        savings = income - total_expenses
        savings_rate = (savings / income) * 100 if income > 0 else 0
        
        # Recommended budget percentages (50/30/20 rule)
        recommended = {
            'needs': income * 0.50,
            'wants': income * 0.30,
            'savings': income * 0.20
        }
        
        # Categorize expenses
        needs_categories = ['rent', 'utilities', 'groceries', 'transportation', 'insurance', 'minimum_debt_payments']
        wants_categories = ['dining_out', 'entertainment', 'shopping', 'hobbies', 'subscriptions']
        
        needs_total = sum(expenses.get(cat, 0) for cat in needs_categories)
        wants_total = sum(expenses.get(cat, 0) for cat in wants_categories)
        
        return {
            'total_income': income,
            'total_expenses': total_expenses,
            'savings': savings,
            'savings_rate': savings_rate,
            'needs_spending': needs_total,
            'wants_spending': wants_total,
            'recommended': recommended,
            'budget_health': self._assess_budget_health(savings_rate, needs_total, wants_total, income)
        }
    
    def _assess_budget_health(self, savings_rate: float, needs: float, wants: float, income: float) -> str:
        """Assess overall budget health"""
        if savings_rate >= 20:
            return "excellent"
        elif savings_rate >= 10:
            return "good"
        elif savings_rate >= 5:
            return "fair"
        else:
            return "needs_improvement"
    
    def generate_investment_suggestions(self, user_profile: UserProfile, available_funds: float) -> List[Dict]:
        """Generate investment suggestions based on user profile"""
        suggestions = []
        
        if user_profile.user_type == 'student':
            suggestions.extend([
                {
                    'type': 'High-Yield Savings Account',
                    'allocation': min(available_funds, 5000),
                    'reason': 'Build emergency fund with easy access',
                    'risk_level': 'Very Low',
                    'expected_return': '4-5% APY'
                },
                {
                    'type': 'Index Fund (S&P 500)',
                    'allocation': available_funds * 0.7,
                    'reason': 'Long-term growth with diversification',
                    'risk_level': 'Moderate',
                    'expected_return': '8-10% annually'
                }
            ])
        else:  # professional
            if user_profile.risk_tolerance == 'low':
                suggestions.extend([
                    {
                        'type': 'Bond Index Fund',
                        'allocation': available_funds * 0.4,
                        'reason': 'Stable income with lower volatility',
                        'risk_level': 'Low',
                        'expected_return': '3-5% annually'
                    },
                    {
                        'type': 'Dividend Growth Fund',
                        'allocation': available_funds * 0.6,
                        'reason': 'Regular income with growth potential',
                        'risk_level': 'Moderate',
                        'expected_return': '6-8% annually'
                    }
                ])
            elif user_profile.risk_tolerance == 'high':
                suggestions.extend([
                    {
                        'type': 'Growth Stock Index',
                        'allocation': available_funds * 0.7,
                        'reason': 'Higher growth potential for long-term wealth building',
                        'risk_level': 'High',
                        'expected_return': '10-12% annually'
                    },
                    {
                        'type': 'International Fund',
                        'allocation': available_funds * 0.3,
                        'reason': 'Geographic diversification',
                        'risk_level': 'Moderate-High',
                        'expected_return': '8-10% annually'
                    }
                ])
        
        return suggestions

class ResponseGenerator:
    """Generate contextual responses based on user type and query"""
    
    def __init__(self):
        self.tone_styles = {
            'student': {
                'greeting': "Hey there! 👋",
                'complexity': 'simple',
                'examples': 'relatable_student',
                'encouragement': 'motivational'
            },
            'professional': {
                'greeting': "Good day,",
                'complexity': 'detailed',
                'examples': 'career_focused',
                'encouragement': 'strategic'
            }
        }
    
    def adapt_tone(self, message: str, user_type: str) -> str:
        """Adapt message tone based on user type"""
        style = self.tone_styles.get(user_type, self.tone_styles['professional'])
        
        if user_type == 'student':
            # Make it more casual and encouraging
            message = message.replace("You should", "You might want to")
            message = message.replace("It is recommended", "It's a good idea to")
            message = re.sub(r'\$(\d+)', r'$\1 (that\'s like \1 cups of coffee! ☕)', message)
        
        return message
    
    def generate_budget_summary(self, analysis: Dict, user_profile: UserProfile) -> str:
        """Generate a comprehensive budget summary"""
        user_type = user_profile.user_type
        
        summary = f"""
{self.tone_styles[user_type]['greeting']} Here's your budget analysis:

💰 **Income & Spending Overview**
• Monthly Income: ${analysis['total_income']:,.2f}
• Total Expenses: ${analysis['total_expenses']:,.2f}
• Monthly Savings: ${analysis['savings']:,.2f}
• Savings Rate: {analysis['savings_rate']:.1f}%

📊 **Budget Breakdown**
• Needs (Housing, Food, Transport): ${analysis['needs_spending']:,.2f}
• Wants (Entertainment, Shopping): ${analysis['wants_spending']:,.2f}
• Recommended Savings Target: ${analysis['recommended']['savings']:,.2f} (20% of income)

🎯 **Budget Health: {analysis['budget_health'].replace('_', ' ').title()}**
"""
        
        if analysis['budget_health'] == 'excellent':
            summary += "\n🌟 Outstanding work! You're exceeding savings goals."
        elif analysis['budget_health'] == 'needs_improvement':
            summary += "\n⚠️  Let's work on boosting that savings rate. Small changes can make a big difference!"
        
        return self.adapt_tone(summary, user_type)
    
    def generate_spending_insights(self, expenses: Dict[str, float], user_profile: UserProfile) -> List[str]:
        """Generate actionable spending insights"""
        insights = []
        total_expenses = sum(expenses.values())
        
        # Find highest expense categories
        sorted_expenses = sorted(expenses.items(), key=lambda x: x[1], reverse=True)
        
        if len(sorted_expenses) > 0:
            highest_category, highest_amount = sorted_expenses[0]
            percentage = (highest_amount / total_expenses) * 100
            
            insights.append(f"Your highest expense is {highest_category}: ${highest_amount:,.2f} ({percentage:.1f}% of total spending)")
            
            # Provide category-specific advice
            if highest_category in ['dining_out', 'entertainment']:
                if user_profile.user_type == 'student':
                    insights.append("💡 Try cooking more meals at home or finding free campus activities to reduce this expense.")
                else:
                    insights.append("💡 Consider meal prepping or setting a monthly entertainment budget to control this expense.")
            
            elif highest_category == 'rent':
                if percentage > 30:
                    insights.append("⚠️  Housing costs exceed the recommended 30% of income. Consider roommates or relocating if possible.")
        
        # Look for opportunities
        if 'subscriptions' in expenses and expenses['subscriptions'] > 50:
            insights.append("🔍 Review subscriptions - you might have services you're not using regularly.")
        
        return [self.adapt_tone(insight, user_profile.user_type) for insight in insights]

class PersonalFinanceChatbot:
    """Main chatbot class orchestrating all components"""
    
    def __init__(self):
        self.analyzer = FinancialAnalyzer()
        self.response_generator = ResponseGenerator()
        self.user_profiles = {}  # In production, this would be a database
        self.conversation_history = {}
    
    def create_user_profile(self, user_id: str, user_type: str, age: int, **kwargs) -> UserProfile:
        """Create and store user profile"""
        profile = UserProfile(
            user_type=user_type,
            age=age,
            **kwargs
        )
        self.user_profiles[user_id] = profile
        return profile
    
    def update_user_expenses(self, user_id: str, expenses: Dict[str, float]):
        """Update user expense data"""
        if user_id in self.user_profiles:
            self.user_profiles[user_id].expenses.update(expenses)
    
    def process_query(self, user_id: str, query: str) -> str:
        """Process user query and generate response"""
        if user_id not in self.user_profiles:
            return "Please create your profile first using create_profile()."
        
        user_profile = self.user_profiles[user_id]
        query_lower = query.lower()
        
        try:
            if any(word in query_lower for word in ['tax', 'taxes', 'federal']):
                return self._handle_tax_query(user_profile, query)
            
            elif any(word in query_lower for word in ['budget', 'spending', 'expenses']):
                return self._handle_budget_query(user_profile, query)
            
            elif any(word in query_lower for word in ['invest', 'investment', 'portfolio']):
                return self._handle_investment_query(user_profile, query)
            
            elif any(word in query_lower for word in ['save', 'savings', 'emergency fund']):
                return self._handle_savings_query(user_profile, query)
            
            else:
                return self._handle_general_query(user_profile, query)
        
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return "I'm sorry, I encountered an error processing your request. Please try again."
    
    def _handle_tax_query(self, user_profile: UserProfile, query: str) -> str:
        """Handle tax-related queries"""
        if not user_profile.income:
            return "I need your income information to calculate taxes. Please update your profile with your annual income."
        
        tax_analysis = self.analyzer.calculate_tax_estimate(user_profile.income)
        
        response = f"""
📋 **Tax Estimate for ${user_profile.income:,.0f} Annual Income**

• Estimated Federal Tax: ${tax_analysis['total_tax']:,.2f}
• Effective Tax Rate: {tax_analysis['effective_rate']:.1f}%
• After-Tax Income: ${tax_analysis['after_tax_income']:,.2f}

💡 **Tax Planning Tips:**
"""
        
        if user_profile.user_type == 'student':
            response += """
• Claim education credits (American Opportunity Credit up to $2,500)
• Keep receipts for textbooks and school supplies
• Consider a part-time job for work-study benefits
"""
        else:
            response += """
• Maximize 401(k) contributions to reduce taxable income
• Consider HSA contributions if available
• Track business expenses if self-employed
• Review tax-loss harvesting for investments
"""
        
        return self.response_generator.adapt_tone(response, user_profile.user_type)
    
    def _handle_budget_query(self, user_profile: UserProfile, query: str) -> str:
        """Handle budget-related queries"""
        if not user_profile.income or not user_profile.expenses:
            return "I need your income and expense information to analyze your budget. Please update your profile."
        
        budget_analysis = self.analyzer.analyze_budget(user_profile.income, user_profile.expenses)
        budget_summary = self.response_generator.generate_budget_summary(budget_analysis, user_profile)
        spending_insights = self.response_generator.generate_spending_insights(user_profile.expenses, user_profile)
        
        response = budget_summary + "\n\n🔍 **Spending Insights:**\n"
        for insight in spending_insights[:3]:  # Limit to top 3 insights
            response += f"• {insight}\n"
        
        return response
    
    def _handle_investment_query(self, user_profile: UserProfile, query: str) -> str:
        """Handle investment-related queries"""
        if not user_profile.income:
            return "I need your income information to provide investment advice. Please update your profile."
        
        # Calculate available funds for investment (assuming 20% of income after expenses)
        total_expenses = sum(user_profile.expenses.values()) if user_profile.expenses else user_profile.income * 0.8
        available_funds = max(0, (user_profile.income - total_expenses) * 0.8)  # 80% of savings for investments
        
        if available_funds < 100:
            return self.response_generator.adapt_tone(
                "Focus on building an emergency fund first before investing. Aim to save at least $1,000 for emergencies.",
                user_profile.user_type
            )
        
        suggestions = self.analyzer.generate_investment_suggestions(user_profile, available_funds)
        
        response = f"🚀 **Investment Suggestions for ${available_funds:,.0f}**\n\n"
        
        for suggestion in suggestions:
            response += f"""
**{suggestion['type']}**
• Suggested Amount: ${suggestion['allocation']:,.0f}
• Risk Level: {suggestion['risk_level']}
• Expected Return: {suggestion['expected_return']}
• Why: {suggestion['reason']}

"""
        
        response += "\n⚠️  Remember: Past performance doesn't guarantee future results. Consider consulting a financial advisor for personalized advice."
        
        return self.response_generator.adapt_tone(response, user_profile.user_type)
    
    def _handle_savings_query(self, user_profile: UserProfile, query: str) -> str:
        """Handle savings-related queries"""
        emergency_fund_target = (sum(user_profile.expenses.values()) if user_profile.expenses else user_profile.income * 0.7) * 6
        
        response = f"""
🏦 **Savings Strategy**

**Emergency Fund Goal:** ${emergency_fund_target:,.0f}
(6 months of expenses)

**Recommended Savings Accounts:**
• High-Yield Savings: 4-5% APY
• Money Market Account: 3-4% APY
• CDs: 4-5% APY (if you won't need the money soon)

"""
        
        if user_profile.user_type == 'student':
            response += """
**Student-Specific Tips:**
• Start with $1,000 emergency fund
• Use cashback credit cards responsibly
• Take advantage of student discounts
• Consider part-time work or internships
"""
        else:
            response += """
**Professional Tips:**
• Automate savings transfers
• Save tax refunds and bonuses
• Consider employer 401(k) match as "free money"
• Set up separate accounts for different goals
"""
        
        return self.response_generator.adapt_tone(response, user_profile.user_type)
    
    def _handle_general_query(self, user_profile: UserProfile, query: str) -> str:
        """Handle general financial queries"""
        general_advice = {
            'student': """
🎓 **General Financial Tips for Students:**

• Create a simple budget with your income (jobs, financial aid)
• Build credit responsibly with a student credit card
• Take advantage of student discounts everywhere
• Start an emergency fund, even if it's just $20/month
• Learn about investing early - time is your biggest advantage
• Avoid unnecessary debt beyond student loans
""",
            'professional': """
💼 **General Financial Tips for Professionals:**

• Follow the 50/30/20 rule (needs/wants/savings)
• Maximize employer 401(k) match
• Build 3-6 months emergency fund
• Diversify investments across asset classes
• Review and optimize insurance coverage
• Plan for major life events (house, family, retirement)
• Consider tax-advantaged accounts (HSA, IRA)
"""
        }
        
        response = general_advice.get(user_profile.user_type, general_advice['professional'])
        return self.response_generator.adapt_tone(response, user_profile.user_type)
    
    def get_user_profile_summary(self, user_id: str) -> str:
        """Get formatted user profile summary"""
        if user_id not in self.user_profiles:
            return "No profile found."
        
        profile = self.user_profiles[user_id]
        summary = f"""
👤 **Profile Summary**
• User Type: {profile.user_type.title()}
• Age: {profile.age}
• Income: ${profile.income:,.2f}/year" if profile.income else "Not set"
• Risk Tolerance: {profile.risk_tolerance.title()}
"""
        
        if profile.expenses:
            summary += f"• Monthly Expenses: ${sum(profile.expenses.values()):,.2f}"
        
        return summary

# Example usage and testing
def main():
    """Example usage of the Personal Finance Chatbot"""
    chatbot = PersonalFinanceChatbot()
    
    # Create sample user profiles
    print("=== Creating Sample User Profiles ===")
    
    # Student profile
    student_profile = chatbot.create_user_profile(
        user_id="student_123",
        user_type="student",
        age=20,
        income=15000,  # Part-time job + financial aid
        expenses={
            "rent": 600,
            "groceries": 200,
            "transportation": 100,
            "entertainment": 150,
            "textbooks": 50
        },
        risk_tolerance="moderate"
    )
    
    # Professional profile
    professional_profile = chatbot.create_user_profile(
        user_id="prof_456",
        user_type="professional",
        age=28,
        income=75000,
        expenses={
            "rent": 1500,
            "groceries": 400,
            "transportation": 300,
            "dining_out": 300,
            "entertainment": 200,
            "subscriptions": 100,
            "insurance": 200
        },
        risk_tolerance="high"
    )
    
    # Test queries
    print("\n=== Testing Student Queries ===")
    test_queries_student = [
        "How much will I pay in taxes?",
        "Can you analyze my budget?",
        "What should I invest in?",
        "How should I save money?"
    ]
    
    for query in test_queries_student:
        print(f"\n🔵 Query: {query}")
        response = chatbot.process_query("student_123", query)
        print(response)
        print("-" * 50)
    
    print("\n=== Testing Professional Queries ===")
    test_queries_professional = [
        "What's my tax situation?",
        "Give me a budget analysis",
        "Investment recommendations please",
        "General financial advice"
    ]
    
    for query in test_queries_professional:
        print(f"\n🔵 Query: {query}")
        response = chatbot.process_query("prof_456", query)
        print(response)
        print("-" * 50)
    
    # Display profiles
    print("\n=== User Profile Summaries ===")
    print("Student Profile:")
    print(chatbot.get_user_profile_summary("student_123"))
    print("\nProfessional Profile:")
    print(chatbot.get_user_profile_summary("prof_456"))

if __name__ == "__main__":
    main()