import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  Stethoscope, 
  Brain, 
  Clock, 
  Shield, 
  TrendingUp, 
  Users, 
  CheckCircle, 
  ArrowRight,
  Play,
  Award,
  Globe,
  Lock,
  Zap,
  Target,
  BarChart3,
  FileText,
  Star,
  ChevronRight,
  Hospital,
  HeartHandshake,
  GraduationCap
} from 'lucide-react'
import clsx from 'clsx'

const testimonials = [
  {
    name: "Dr. Sarah Chen",
    role: "Emergency Medicine Physician",
    hospital: "Seattle General Hospital",
    quote: "DiagnoAssist has transformed my diagnostic workflow. The AI suggestions are remarkably accurate and help me consider differentials I might have missed. It's like having a senior colleague available 24/7.",
    rating: 5,
    avatar: "SC"
  },
  {
    name: "Dr. Michael Rodriguez",
    role: "Internal Medicine",
    hospital: "Mayo Clinic",
    quote: "The dynamic questioning feature is brilliant. It adapts to each patient's presentation and helps me gather more targeted history. My diagnostic confidence has increased significantly.",
    rating: 5,
    avatar: "MR"
  },
  {
    name: "Dr. Jennifer Park",
    role: "Family Medicine",
    hospital: "Johns Hopkins",
    quote: "Time is everything in medicine. DiagnoAssist helps me work through complex cases faster while maintaining accuracy. The test recommendations are spot-on and cost-effective.",
    rating: 5,
    avatar: "JP"
  }
]

const features = [
  {
    icon: Brain,
    title: "AI-Powered Differential Diagnosis",
    description: "Advanced machine learning algorithms analyze patient data to suggest relevant differential diagnoses with confidence scoring.",
    color: "bg-blue-500"
  },
  {
    icon: Target,
    title: "Dynamic Clinical Assessment",
    description: "Intelligent questioning system that adapts based on patient responses, ensuring comprehensive data collection.",
    color: "bg-purple-500"
  },
  {
    icon: BarChart3,
    title: "Smart Test Recommendations",
    description: "Evidence-based suggestions for diagnostic tests with cost-effectiveness analysis and urgency prioritization.",
    color: "bg-green-500"
  },
  {
    icon: Clock,
    title: "Streamlined Workflow",
    description: "Reduce diagnostic time by 40% while maintaining accuracy through structured, step-by-step clinical protocols.",
    color: "bg-yellow-500"
  },
  {
    icon: Shield,
    title: "HIPAA Compliant",
    description: "Enterprise-grade security with end-to-end encryption, audit trails, and full compliance with healthcare regulations.",
    color: "bg-red-500"
  },
  {
    icon: FileText,
    title: "Comprehensive Documentation",
    description: "Automated generation of clinical notes, treatment plans, and follow-up instructions with full customization.",
    color: "bg-indigo-500"
  }
]

const stats = [
  { label: "Diagnostic Accuracy", value: "94.2%", change: "+3.8%" },
  { label: "Time Reduction", value: "42%", change: "+12%" },
  { label: "Active Physicians", value: "15,000+", change: "+2,400" },
  { label: "Cases Processed", value: "2.3M", change: "+45%" }
]

const plans = [
  {
    name: "Starter",
    price: "$99",
    period: "/month",
    description: "Perfect for individual practitioners",
    features: [
      "Up to 100 cases/month",
      "Basic AI diagnostics",
      "Standard reporting",
      "Email support",
      "HIPAA compliance"
    ],
    popular: false
  },
  {
    name: "Professional",
    price: "$249",
    period: "/month",
    description: "For busy medical practices",
    features: [
      "Up to 500 cases/month",
      "Advanced AI diagnostics",
      "Custom templates",
      "Priority support",
      "API integration",
      "Advanced analytics"
    ],
    popular: true
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "pricing",
    description: "For hospitals and health systems",
    features: [
      "Unlimited cases",
      "Custom AI training",
      "White-label option",
      "Dedicated support",
      "EHR integration",
      "Advanced security"
    ],
    popular: false
  }
]

export default function LandingPage() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('overview')

  const handleStartDemo = () => {
    navigate('/app/patient-info')
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-blue-600 rounded-lg">
                <Stethoscope className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">DiagnoAssist</h1>
                <p className="text-xs text-gray-600">AI-Powered Diagnostics</p>
              </div>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-600 hover:text-gray-900">Features</a>
              <a href="#workflow" className="text-gray-600 hover:text-gray-900">Workflow</a>
              <a href="#testimonials" className="text-gray-600 hover:text-gray-900">Testimonials</a>
              <a href="#pricing" className="text-gray-600 hover:text-gray-900">Pricing</a>
            </div>
            
            <div className="flex items-center space-x-4">
              <button className="text-gray-600 hover:text-gray-900">Sign In</button>
              <button 
                onClick={handleStartDemo}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Start Demo
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-50 via-white to-purple-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="flex items-center space-x-2 mb-6">
                <Award className="w-5 h-5 text-blue-600" />
                <span className="text-blue-600 font-medium">Trusted by 15,000+ physicians worldwide</span>
              </div>
              
              <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
                AI-Powered
                <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> Diagnostic </span>
                Excellence
              </h1>
              
              <p className="text-xl text-gray-600 mb-8 leading-relaxed">
                Enhance your clinical decision-making with advanced AI that analyzes patient data, 
                suggests differential diagnoses, and streamlines your workflow—all while maintaining 
                the highest standards of medical accuracy and patient safety.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <button 
                  onClick={handleStartDemo}
                  className="flex items-center justify-center space-x-2 bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 transition-colors font-semibold text-lg"
                >
                  <Play className="w-5 h-5" />
                  <span>Try Interactive Demo</span>
                </button>
                <button className="flex items-center justify-center space-x-2 border border-gray-300 text-gray-700 px-8 py-4 rounded-lg hover:bg-gray-50 transition-colors font-semibold">
                  <span>Schedule Demo</span>
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>
              
              <div className="flex items-center space-x-6 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span>HIPAA Compliant</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span>FDA Cleared</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span>24/7 Support</span>
                </div>
              </div>
            </div>
            
            <div className="relative">
              <div className="bg-white rounded-2xl shadow-2xl p-8 border border-gray-200">
                <div className="mb-6">
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Brain className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">AI Analysis Complete</h3>
                      <p className="text-sm text-gray-600">Confidence: 94.2%</p>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                      <span className="font-medium text-green-800">Community-Acquired Pneumonia</span>
                      <span className="text-green-700 font-bold">90%</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                      <span className="font-medium text-yellow-800">Acute Bronchitis</span>
                      <span className="text-yellow-700 font-bold">65%</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <span className="font-medium text-blue-800">Viral Upper Respiratory Infection</span>
                      <span className="text-blue-700 font-bold">45%</span>
                    </div>
                  </div>
                </div>
                
                <div className="border-t border-gray-200 pt-6">
                  <h4 className="font-semibold text-gray-900 mb-3">Recommended Tests</h4>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2 text-sm">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span>Chest X-Ray (High Priority)</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span>CBC with Differential</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span>Blood Cultures</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="absolute -top-4 -right-4 bg-green-500 text-white p-3 rounded-full">
                <Zap className="w-6 h-6" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl font-bold text-gray-900 mb-2">{stat.value}</div>
                <div className="text-gray-600 mb-1">{stat.label}</div>
                <div className="text-green-600 text-sm font-medium">{stat.change} this month</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Intelligent Features for Modern Medicine
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Powered by advanced machine learning and designed by medical professionals, 
              DiagnoAssist enhances every aspect of your diagnostic workflow.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-white p-8 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
                <div className={clsx("w-12 h-12 rounded-lg flex items-center justify-center mb-6", feature.color)}>
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Workflow Section */}
      <section id="workflow" className="py-20 bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Streamlined Clinical Workflow
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Follow our evidence-based, six-step diagnostic process that integrates seamlessly 
              with your existing clinical practice.
            </p>
          </div>
          
          {/* Workflow Steps */}
          <div className="relative">
            {/* Background connecting line */}
            <div className="hidden lg:block absolute top-8 left-0 right-0 h-1 bg-blue-200" style={{ left: '4rem', right: '4rem' }}></div>
            
            {/* Steps Container */}
            <div className="flex justify-between items-start max-w-6xl mx-auto relative">
              {[
                {
                  step: "01",
                  title: "Patient Assessment",
                  description: "Dynamic questioning and medical history collection with AI-powered follow-ups",
                  icon: Users
                },
                {
                  step: "02", 
                  title: "Physical Examination",
                  description: "Structured vital signs and system-specific examination findings",
                  icon: Stethoscope
                },
                {
                  step: "03",
                  title: "AI Diagnostic Analysis", 
                  description: "Machine learning generates differential diagnoses with confidence scoring",
                  icon: Brain
                },
                {
                  step: "04",
                  title: "Test Recommendations",
                  description: "Evidence-based diagnostic test suggestions with cost-effectiveness analysis",
                  icon: BarChart3
                },
                {
                  step: "05",
                  title: "Results Integration",
                  description: "Structured input for laboratory and imaging results with interpretation",
                  icon: FileText
                },
                {
                  step: "06",
                  title: "Final Diagnosis",
                  description: "Refined analysis with treatment planning and documentation generation",
                  icon: Target
                }
              ].map((step, index) => (
                <div key={index} className="relative flex flex-col items-center text-center group flex-1">
                  {/* Step Circle */}
                  <div className="relative z-10 w-16 h-16 bg-white border-4 border-blue-600 rounded-full flex items-center justify-center mb-4 group-hover:bg-blue-600 group-hover:border-blue-700 transition-colors duration-300">
                    <step.icon className="w-6 h-6 text-blue-600 group-hover:text-white transition-colors duration-300" />
                  </div>
                  
                  {/* Step Number Badge */}
                  <div className="absolute -top-1 -right-1 z-20 w-7 h-7 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-xs border-3 border-white group-hover:bg-blue-700 transition-colors duration-300">
                    {step.step}
                  </div>
                  
                  {/* Step Content */}
                  <div className="max-w-36">
                    <h3 className="text-sm lg:text-base font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors duration-300">
                      {step.title}
                    </h3>
                    <p className="text-xs lg:text-sm text-gray-600 leading-relaxed hidden lg:block">
                      {step.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Mobile Workflow - Vertical */}
            <div className="lg:hidden space-y-8 mt-8">
              {[
                {
                  step: "01",
                  title: "Patient Assessment",
                  description: "Dynamic questioning and medical history collection with AI-powered follow-ups",
                  icon: Users
                },
                {
                  step: "02", 
                  title: "Physical Examination",
                  description: "Structured vital signs and system-specific examination findings",
                  icon: Stethoscope
                },
                {
                  step: "03",
                  title: "AI Diagnostic Analysis", 
                  description: "Machine learning generates differential diagnoses with confidence scoring",
                  icon: Brain
                },
                {
                  step: "04",
                  title: "Test Recommendations",
                  description: "Evidence-based diagnostic test suggestions with cost-effectiveness analysis",
                  icon: BarChart3
                },
                {
                  step: "05",
                  title: "Results Integration",
                  description: "Structured input for laboratory and imaging results with interpretation",
                  icon: FileText
                },
                {
                  step: "06",
                  title: "Final Diagnosis",
                  description: "Refined analysis with treatment planning and documentation generation",
                  icon: Target
                }
              ].map((step, index) => (
                <div key={index} className="relative flex items-center space-x-4">
                  {/* Connecting Line - Vertical */}
                  {index < 5 && (
                    <div className="absolute top-16 left-8 w-1 h-8 bg-blue-300"></div>
                  )}
                  
                  {/* Step Circle */}
                  <div className="relative z-10 w-16 h-16 bg-white border-4 border-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <step.icon className="w-6 h-6 text-blue-600" />
                  </div>
                  
                  {/* Step Number Badge */}
                  <div className="absolute left-12 top-0 z-20 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-xs border-2 border-white">
                    {step.step}
                  </div>
                  
                  {/* Step Content */}
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{step.title}</h3>
                    <p className="text-sm text-gray-600 leading-relaxed">{step.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="text-center mt-12">
            <button 
              onClick={handleStartDemo}
              className="bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 transition-colors font-semibold text-lg"
            >
              Experience the Workflow
            </button>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Trusted by Medical Professionals
            </h2>
            <p className="text-xl text-gray-600">
              See why thousands of physicians rely on DiagnoAssist for better patient outcomes
            </p>
          </div>
          
          <div className="grid lg:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-white p-8 rounded-xl shadow-lg border border-gray-200">
                <div className="flex items-center mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <blockquote className="text-gray-700 mb-6 italic">
                  "{testimonial.quote}"
                </blockquote>
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold mr-4">
                    {testimonial.avatar}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">{testimonial.name}</div>
                    <div className="text-gray-600 text-sm">{testimonial.role}</div>
                    <div className="text-gray-500 text-sm">{testimonial.hospital}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Choose Your Plan
            </h2>
            <p className="text-xl text-gray-600">
              Flexible pricing options for practices of all sizes
            </p>
          </div>
          
          <div className="grid lg:grid-cols-3 gap-8">
            {plans.map((plan, index) => (
              <div key={index} className={clsx(
                "bg-white p-8 rounded-xl shadow-lg border-2 relative",
                plan.popular ? "border-blue-500" : "border-gray-200"
              )}>
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                    Most Popular
                  </div>
                )}
                
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <p className="text-gray-600 mb-4">{plan.description}</p>
                  <div className="flex items-baseline justify-center">
                    <span className="text-4xl font-bold text-gray-900">{plan.price}</span>
                    <span className="text-gray-600 ml-1">{plan.period}</span>
                  </div>
                </div>
                
                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <button className={clsx(
                  "w-full py-3 px-6 rounded-lg font-semibold transition-colors",
                  plan.popular 
                    ? "bg-blue-600 text-white hover:bg-blue-700" 
                    : "bg-gray-100 text-gray-900 hover:bg-gray-200"
                )}>
                  {plan.name === "Enterprise" ? "Contact Sales" : "Start Free Trial"}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Transform Your Practice?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of physicians who are already using DiagnoAssist to improve 
            patient outcomes and streamline their diagnostic workflow.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={handleStartDemo}
              className="bg-white text-blue-600 px-8 py-4 rounded-lg hover:bg-gray-100 transition-colors font-semibold text-lg"
            >
              Start Free Demo
            </button>
            <button className="border-2 border-white text-white px-8 py-4 rounded-lg hover:bg-white hover:text-blue-600 transition-colors font-semibold">
              Schedule Consultation
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-3 mb-6">
                <div className="flex items-center justify-center w-10 h-10 bg-blue-600 rounded-lg">
                  <Stethoscope className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold">DiagnoAssist</h3>
                  <p className="text-sm text-gray-400">AI-Powered Diagnostics</p>
                </div>
              </div>
              <p className="text-gray-400 text-sm leading-relaxed">
                Enhancing clinical decision-making with advanced AI technology, 
                designed by medical professionals for medical professionals.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white">Features</a></li>
                <li><a href="#" className="hover:text-white">Pricing</a></li>
                <li><a href="#" className="hover:text-white">API Documentation</a></li>
                <li><a href="#" className="hover:text-white">Integration</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white">About Us</a></li>
                <li><a href="#" className="hover:text-white">Careers</a></li>
                <li><a href="#" className="hover:text-white">Research</a></li>
                <li><a href="#" className="hover:text-white">Press</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white">Help Center</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
                <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white">Terms of Service</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 text-sm">
              © 2024 DiagnoAssist. All rights reserved.
            </p>
            <div className="flex items-center space-x-6 mt-4 md:mt-0">
              <div className="flex items-center space-x-2 text-sm text-gray-400">
                <Lock className="w-4 h-4" />
                <span>HIPAA Compliant</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-gray-400">
                <Shield className="w-4 h-4" />
                <span>FDA Cleared</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}