"""
AI-Powered Insights Generator for Pulselytics
Uses OpenAI GPT to generate automated insights, recommendations, and trend analysis
"""
import os
import json
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not installed. Run: pip install openai")


class AIInsightsGenerator:
    """Generate AI-powered insights using OpenAI GPT"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI insights generator
        
        Args:
            api_key: OpenAI API key (if not provided, will look for OPENAI_API_KEY env var)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed")
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_insights(self, analytics_data: Dict) -> Dict:
        """
        Generate comprehensive AI insights from analytics data
        
        Args:
            analytics_data: Dictionary containing analytics metrics
            
        Returns:
            Dictionary with AI-generated insights
        """
        try:
            # Prepare data summary for GPT
            data_summary = self._prepare_data_summary(analytics_data)
            
            # Generate insights using GPT
            prompt = self._build_insights_prompt(data_summary)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert social media analytics consultant. Provide actionable insights and recommendations based on the data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            insights_text = response.choices[0].message.content
            
            return {
                'success': True,
                'insights': insights_text,
                'key_findings': self._extract_key_findings(insights_text),
                'recommendations': self._extract_recommendations(insights_text),
                'generated_at': datetime.now().isoformat(),
                'source': 'openai'
            }
            
        except Exception as e:
            # Re-raise the exception so fallback can handle it
            raise e
    
    def generate_content_recommendations(self, top_posts: List[Dict], platforms: List[Dict]) -> Dict:
        """
        Generate content recommendations based on top performing posts
        
        Args:
            top_posts: List of top performing posts
            platforms: Platform distribution data
            
        Returns:
            Dictionary with content recommendations
        """
        try:
            prompt = f"""Based on the following top performing posts, provide specific content recommendations:

Top Posts:
{json.dumps(top_posts[:5], indent=2)}

Platform Distribution:
{json.dumps(platforms, indent=2)}

Please provide:
1. Content themes that perform best
2. Optimal posting times/frequency suggestions
3. Hashtag strategy recommendations
4. Platform-specific content ideas
5. Engagement optimization tips

Be specific and actionable."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a social media content strategist. Provide specific, actionable recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            recommendations = response.choices[0].message.content
            
            return {
                'success': True,
                'recommendations': recommendations,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_trends(self, trend_data: List[Dict]) -> Dict:
        """
        Analyze engagement trends and predict future performance
        
        Args:
            trend_data: Time-series engagement data
            
        Returns:
            Dictionary with trend analysis
        """
        try:
            if not trend_data:
                return {'success': False, 'error': 'No trend data provided'}
            
            # Calculate trend metrics
            df = pd.DataFrame(trend_data)
            if 'engagement' in df.columns:
                recent_avg = df.tail(7)['engagement'].mean()
                overall_avg = df['engagement'].mean()
                trend_direction = "increasing" if recent_avg > overall_avg else "decreasing"
                change_pct = ((recent_avg - overall_avg) / overall_avg * 100) if overall_avg > 0 else 0
            else:
                recent_avg = 0
                overall_avg = 0
                trend_direction = "stable"
                change_pct = 0
            
            prompt = f"""Analyze this engagement trend data and provide insights:

Trend Data Summary:
- Recent 7-day average: {recent_avg:.0f}
- Overall average: {overall_avg:.0f}
- Trend: {trend_direction}
- Change: {change_pct:.1f}%

Data Points:
{json.dumps(trend_data[-14:], indent=2)}

Provide:
1. Trend interpretation
2. Contributing factors
3. Predictions for next 30 days
4. Actionable recommendations to improve trends"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a data analyst specializing in social media metrics."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            analysis = response.choices[0].message.content
            
            return {
                'success': True,
                'analysis': analysis,
                'trend_direction': trend_direction,
                'change_percentage': round(change_pct, 1),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _prepare_data_summary(self, data: Dict) -> str:
        """Prepare a concise summary of analytics data for GPT"""
        summary = f"""
Analytics Summary:
- Total Posts: {data.get('total_posts', 0)}
- Average Likes: {data.get('avg_likes', 0):.1f}
- Average Comments: {data.get('avg_comments', 0):.1f}
- Average Views: {data.get('avg_views', 0):.0f}
- Platforms: {', '.join([p['platform'] for p in data.get('platforms', [])])}
- Top Hashtags: {', '.join(['#' + h['hashtag'] for h in data.get('hashtags', [])[:5]])}
"""
        return summary
    
    def _build_insights_prompt(self, data_summary: str) -> str:
        """Build the prompt for insights generation"""
        return f"""{data_summary}

Based on this social media analytics data, provide:

1. **Key Performance Highlights**: What's working well?
2. **Areas for Improvement**: What needs attention?
3. **Strategic Recommendations**: 3-5 specific actionable steps
4. **Platform Strategy**: Platform-specific insights
5. **Content Strategy**: What content types to focus on

Be specific, data-driven, and actionable. Format your response clearly."""
    
    def _extract_key_findings(self, insights: str) -> List[str]:
        """Extract key findings from insights text"""
        # Simple extraction - look for numbered or bulleted points
        findings = []
        lines = insights.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Clean up numbering and bullets
                clean_line = line.lstrip('0123456789.-•) ').strip()
                if len(clean_line) > 10:  # Meaningful finding
                    findings.append(clean_line)
        return findings[:5]  # Top 5 findings
    
    def _extract_recommendations(self, insights: str) -> List[str]:
        """Extract actionable recommendations from insights text"""
        # Look for recommendation section
        recommendations = []
        in_rec_section = False
        lines = insights.split('\n')
        
        for line in lines:
            line = line.strip()
            if 'recommendation' in line.lower() or 'action' in line.lower():
                in_rec_section = True
                continue
            
            if in_rec_section and line:
                if line[0].isdigit() or line.startswith('-') or line.startswith('•'):
                    clean_line = line.lstrip('0123456789.-•) ').strip()
                    if len(clean_line) > 10:
                        recommendations.append(clean_line)
                elif len(recommendations) >= 3:  # Got enough recommendations
                    break
        
        return recommendations[:5]


def generate_quick_insights(analytics_data: Dict, use_fallback: bool = True) -> Dict:
    """
    Generate insights with fallback to rule-based system if OpenAI unavailable
    
    Args:
        analytics_data: Analytics data dictionary
        use_fallback: Whether to use fallback if OpenAI fails
        
    Returns:
        Dictionary with insights
    """
    api_key = os.getenv('OPENAI_API_KEY')
    
    if OPENAI_AVAILABLE and api_key:
        try:
            generator = AIInsightsGenerator(api_key)
            return generator.generate_insights(analytics_data)
        except Exception as e:
            if not use_fallback:
                return {'success': False, 'error': str(e)}
            print(f"AI insights failed, using fallback: {e}")
    
    # Fallback: Rule-based insights
    insights = []
    recommendations = []
    trends = []
    warnings = []
    
    total_posts = analytics_data.get('total_posts', 0)
    avg_likes = analytics_data.get('avg_likes', 0)
    avg_comments = analytics_data.get('avg_comments', 0)
    avg_views = analytics_data.get('avg_views', 0)
    platforms = analytics_data.get('platforms', [])
    top_posts = analytics_data.get('top_posts', [])
    trend_data = analytics_data.get('trend', [])
    
    # Analyze posting frequency
    if total_posts > 100:
        insights.append(f"Strong content output with {total_posts} posts analyzed")
        trends.append("Consistent posting schedule established")
    elif total_posts < 20:
        insights.append(f"Low post volume detected ({total_posts} posts)")
        warnings.append("Increase posting frequency to maintain audience engagement")
        recommendations.append("Aim for 3-5 posts per week per platform for optimal growth")
    else:
        insights.append(f"Moderate posting activity with {total_posts} posts")
        recommendations.append("Consider increasing posting frequency for better visibility")
    
    # Analyze engagement
    if avg_likes > 1000:
        insights.append(f"Excellent engagement with {avg_likes:.0f} average likes per post")
        trends.append("High audience engagement indicates strong content resonance")
    elif avg_likes > 500:
        insights.append(f"Good engagement with {avg_likes:.0f} average likes")
        recommendations.append("Maintain current content quality and experiment with new formats")
    elif avg_likes < 100:
        insights.append(f"Engagement could be improved (avg {avg_likes:.0f} likes)")
        warnings.append("Low engagement rate compared to posting frequency")
        recommendations.append("Focus on high-quality visual content, compelling captions, and strategic hashtags")
        recommendations.append("Analyze top-performing posts to identify successful patterns")
    
    # Comment engagement
    if avg_comments > 50:
        insights.append(f"Strong community interaction with {avg_comments:.0f} average comments")
        trends.append("Active audience participation indicates loyal community")
    elif avg_comments > 10:
        insights.append(f"Moderate comment engagement ({avg_comments:.0f} avg)")
        recommendations.append("Encourage discussions by asking questions in your posts")
    
    # Platform analysis
    if len(platforms) < 2:
        warnings.append("Limited platform presence may restrict audience reach")
        recommendations.append("Consider expanding to additional platforms (Instagram, YouTube, TikTok, Twitter)")
    elif len(platforms) >= 3:
        insights.append(f"Multi-platform strategy active across {len(platforms)} platforms")
        trends.append("Diversified presence reduces dependency on single platform")
    
    # Best platform
    if platforms:
        best_platform = max(platforms, key=lambda x: x.get('posts', 0))
        platform_name = best_platform.get('platform', 'Unknown').capitalize()
        platform_posts = best_platform.get('posts', 0)
        insights.append(f"{platform_name} is your most active platform with {platform_posts} posts")
        
        if len(platforms) > 1:
            sorted_platforms = sorted(platforms, key=lambda x: x.get('posts', 0), reverse=True)
            second_platform = sorted_platforms[1] if len(sorted_platforms) > 1 else None
            if second_platform:
                second_name = second_platform.get('platform', 'Unknown').capitalize()
                recommendations.append(f"Balance content distribution between {platform_name} and {second_name}")
    
    # General best practices
    recommendations.extend([
        "Post during peak engagement hours: 7-9 AM, 12-1 PM, 7-9 PM local time",
        "Use 5-10 relevant hashtags per post to maximize discoverability",
        "Respond to comments within the first hour to boost algorithmic visibility",
        "Mix content types: photos, videos, stories, and reels for platform variety"
    ])
    
    # Trend analysis
    if trend_data and len(trend_data) > 7:
        recent_engagement = sum(t.get('engagement', 0) for t in trend_data[-7:]) / 7
        older_engagement = sum(t.get('engagement', 0) for t in trend_data[:7]) / 7
        
        if recent_engagement > older_engagement * 1.1:
            trends.append("Engagement is trending upward - continue current strategy")
            insights.append("Recent performance shows positive growth trajectory")
        elif recent_engagement < older_engagement * 0.9:
            trends.append("Engagement declining - strategy adjustment needed")
            warnings.append("Recent engagement drop detected")
            recommendations.append("Review recent content changes and audience feedback")
        else:
            trends.append("Engagement is stable with consistent performance")
    
    return {
        'success': True,
        'key_insights': insights,
        'trends': trends,
        'recommendations': list(set(recommendations))[:8],  # Unique recommendations, max 8
        'warnings': warnings,
        'generated_at': datetime.now().isoformat(),
        'source': 'rule-based'
    }


if __name__ == '__main__':
    # Test with sample data
    sample_data = {
        'total_posts': 156,
        'avg_likes': 4523.5,
        'avg_comments': 234.7,
        'avg_views': 45678,
        'platforms': [
            {'platform': 'instagram', 'posts': 45},
            {'platform': 'youtube', 'posts': 38},
        ],
        'hashtags': [
            {'hashtag': 'fitness', 'count': 23},
            {'hashtag': 'motivation', 'count': 19},
        ]
    }
    
    print("Testing AI Insights Generator...")
    result = generate_quick_insights(sample_data, use_fallback=True)
    
    if result['success']:
        print("\n✅ Insights generated successfully!")
        print("\nKey Findings:")
        for finding in result.get('key_findings', []):
            print(f"  • {finding}")
        print("\nRecommendations:")
        for rec in result.get('recommendations', []):
            print(f"  • {rec}")
    else:
        print(f"\n❌ Error: {result.get('error')}")
