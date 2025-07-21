import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Check, Star, Users, Zap, Clock, Brain, ChartBar, ArrowRight, Sparkles, Calendar, Bell, LogIn } from 'lucide-react';
import SubscriptionModal from './SubscriptionModal';
import DemoDisclaimer from './DemoDisclaimer';
import CountdownTimer from './CountdownTimer';
import { trackVisit, trackClick } from '../../utils/analytics';

const LandingPage = () => {
  const navigate = useNavigate();
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [showDemoDisclaimer, setShowDemoDisclaimer] = useState(false);


  
  const handleSubscribe = (plan) => {
    setSelectedPlan(plan);
    setShowSubscriptionModal(true);
    trackClick('subscribe', plan);
    console.log(plan);
    // fetchStats();

  };
  
  const handleDemo = () => {
    setShowDemoDisclaimer(true);
    trackClick('demo');
    // fetchStats();
  };
  
  const plans = [
    {
      name: 'Starter',
      price: '₱990',
      originalPrice: '₱1,490',
      period: 'per month',
      description: 'Perfect for individual practitioners',
      features: [
        'Up to 50 patients/month',
        'Patient health records',
        'Basic AI diagnosis assistance',
        'Treatment recommendations',
        'Email support',
        'Mobile app access'
      ],
      highlighted: false,
      color: 'gray',
      discount: '33% OFF Early Bird'
    },
    {
      name: 'Professional',
      price: '₱2,490',
      originalPrice: '₱3,990',
      period: 'per month',
      description: 'For growing medical practices',
      features: [
        'Everything in Starter',
        'Up to 200 patients/month',
        'AI audio transcription & analysis',
        'Advanced AI diagnosis',
        'Priority support',
        'Test result integration',
        'Custom report templates',
        'Team collaboration (up to 5 users)'
      ],
      highlighted: true,
      color: 'blue',
      badge: 'Most Popular',
      discount: '38% OFF Early Bird'
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      originalPrice: '',
      period: 'contact us',
      description: 'For hospitals and large clinics',
      features: [
        'Everything in Professional',
        'Unlimited patients',
        'Full AI capabilities',
        'Dedicated account manager',
        'API access',
        'Custom integrations',
        'Unlimited users',
        'On-premise deployment option'
      ],
      highlighted: false,
      color: 'purple',
      discount: 'Special Launch Pricing'
    }
  ];
  
  const features = [
    {
      icon: Brain,
      title: 'AI Diagnosis Assistant',
      description: 'Advanced machine learning algorithms provide diagnostic suggestions while keeping you in full control of medical decisions'
    },
    {
      icon: Clock,
      title: 'Save Time',
      description: 'Reduce diagnosis time by 60% with intelligent patient assessment workflows'
    },
    {
      icon: Activity,
      title: 'AI Audio Transcription',
      description: 'Just press record and your conversation with the patient will automatically be transcribed, analyzed, and organized'
    },
    {
      icon: ChartBar,
      title: 'Analytics Dashboard',
      description: 'Track performance metrics and gain insights into your practice efficiency'
    },
    {
      icon: Users,
      title: 'Patient Health Records',
      description: 'Comprehensive digital health records with smart organization and instant access to patient history'
    },
    {
      icon: Zap,
      title: 'HL7 FHIR Interoperability',
      description: 'Seamlessly integrate with other healthcare systems using the latest cutting-edge interoperability standards'
    }
  ];
  
  const testimonials = [
    {
      name: 'Dr. Sarah Johnson',
      role: 'Family Medicine - Beta Tester',
      content: 'I participated in the beta and DiagnoAssist transformed how I approach patient diagnoses. Can\'t wait for the full launch!',
      rating: 5
    },
    {
      name: 'Dr. Michael Chen',
      role: 'Internal Medicine - Beta Tester',
      content: 'The AI suggestions during beta testing were incredibly accurate. This will be a game-changer for our practice.',
      rating: 5
    },
    {
      name: 'Dr. Emily Rodriguez',
      role: 'Pediatrics - Beta Tester',
      content: 'The clinical decision support is excellent. Looking forward to implementing this in our clinic when it launches.',
      rating: 5
    }
  ];
  
  const faqs = [
    {
      question: 'When will DiagnoAssist officially launch?',
      answer: 'We\'re planning to launch in Q3 2025. Early access members will be the first to get access, starting with a beta period in July 2025.'
    },
    {
      question: 'Will I keep the early bird pricing forever?',
      answer: 'Yes! As an early adopter, you\'ll lock in your discounted rate for as long as you maintain your subscription. This is our way of thanking you for believing in us.'
    },
    {
      question: 'Can I change my plan later?',
      answer: 'Absolutely. You can upgrade or downgrade your plan at any time. If you upgrade, you\'ll still maintain early bird pricing on the new plan.'
    },
    {
      question: 'Is my data secure with DiagnoAssist?',
      answer: 'Security is our top priority. DiagnoAssist is fully HIPAA compliant and uses enterprise-grade encryption for all patient data.'
    },
    {
      question: 'What if I\'m not satisfied after launch?',
      answer: 'We offer a 30-day money-back guarantee after launch. If DiagnoAssist doesn\'t meet your expectations, we\'ll provide a full refund.'
    }
  ];

  useEffect(() => {
    trackVisit();
    // fetchStats();
  }, []);
  
  return (
    <>
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-blue-50 via-white to-purple-50 pb-16">
        {/* Early Bird Banner */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 text-center">
          <p className="text-sm font-medium flex items-center justify-center">
            <Sparkles className="w-4 h-4 mr-2" />
            Limited Time: Early Bird Pricing - Save up to 38% on all plans!
            <Sparkles className="w-4 h-4 ml-2" />
          </p>
        </div>
        
        <nav className="px-8 py-6">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold text-gray-900">DiagnoAssist</span>
            </div>
            <div className="flex items-center space-x-8">
              <a href="#features" className="text-gray-600 hover:text-gray-900 transition-colors">Features</a>
              <a href="#pricing" className="text-gray-600 hover:text-gray-900 transition-colors">Pricing</a>
              <a href="#testimonials" className="text-gray-600 hover:text-gray-900 transition-colors">Testimonials</a>
              <button 
                onClick={handleDemo}
                className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors font-medium"
              >
                See Demo
              </button>
              <button 
                onClick={() => navigate('/dashboard')}
                className="px-6 py-2 bg-gradient-to-r from-gray-600 to-gray-700 text-white rounded-lg hover:from-gray-700 hover:to-gray-800 transition-all duration-300 flex items-center space-x-2"
              >
                <LogIn className="w-4 h-4" />
                <span>Doctor Login</span>
              </button>
              <button 
                onClick={() => handleSubscribe(plans[1])}
                className="px-6 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                Reserve Your Spot
              </button>
            </div>
          </div>
        </nav>
        
        <div className="px-8 py-16">
          <div className="max-w-7xl mx-auto text-center">
            <div className="inline-flex items-center px-4 py-2 bg-purple-100 text-purple-700 rounded-full text-sm font-medium mb-6">
              <Calendar className="w-4 h-4 mr-2" />
              Launching Q3 2025 - Be Among the First!
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Revolutionize Your Medical Practice<br />
              <span className="text-blue-600">with AI-Powered Diagnostics</span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
              Join the waitlist for DiagnoAssist - the cutting-edge AI technology that will transform 
              how healthcare professionals diagnose and treat patients. Reserve your spot now and lock in exclusive early-bird pricing!
            </p>
            <div className="flex justify-center space-x-4 mb-16">
              <button 
                onClick={() => handleSubscribe(plans[1])}
                className="px-8 py-4 bg-blue-600 text-white text-lg font-medium rounded-xl hover:bg-blue-700 transition-all transform hover:scale-105 shadow-lg"
              >
                Reserve Early Access
                <ArrowRight className="inline ml-2 w-5 h-5" />
              </button>
              <button 
                onClick={handleDemo}
                className="px-8 py-4 bg-white text-gray-700 text-lg font-medium rounded-xl hover:bg-gray-50 transition-all border border-gray-300 shadow-md"
              >
                See Demo
              </button>
            </div>
            
            <div className="grid grid-cols-3 gap-8 max-w-4xl mx-auto">
              <div className="text-center">
                <div className="text-4xl font-bold text-blue-600 mb-2">500+</div>
                <div className="text-gray-600">Doctors on Waitlist</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-blue-600 mb-2">₱1M+</div>
                <div className="text-gray-600">Potential Savings/Year</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-blue-600 mb-2">94%</div>
                <div className="text-gray-600">Target Accuracy</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Coming Soon Features */}
      <div className="py-16 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-7xl mx-auto px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-8">
            Why Join the Early Access Program?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-white">
              <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Exclusive Pricing</h3>
              <p className="text-blue-100">Lock in up to 38% discount forever as an early adopter</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-white">
              <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Bell className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Priority Access</h3>
              <p className="text-blue-100">Be among the first to experience AI-powered diagnostics</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-white">
              <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Users className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Shape the Future</h3>
              <p className="text-blue-100">Your feedback will help us build the perfect tool for doctors</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Features Section */}
      <div id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything You Need for Modern Medical Practice
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Revolutionary features designed to enhance your diagnostic capabilities and streamline patient care when we launch
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="p-6 rounded-xl border border-gray-200 hover:border-blue-200 hover:shadow-lg transition-all">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 text-blue-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                  <p className="text-gray-600">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
      
      {/* Pricing Section */}
      <div id="pricing" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Reserve Your Plan with Early Bird Pricing
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-4">
              Be an early adopter and lock in these special rates forever. Limited spots available!
            </p>
            <div className="inline-flex items-center px-4 py-2 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
              <Clock className="w-4 h-4 mr-2" />
              Early bird pricing ends July 31, 2025
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {plans.map((plan, index) => (
              <div
                key={index}
                className={`relative rounded-2xl p-8 ${
                  plan.highlighted 
                    ? 'bg-blue-600 text-white shadow-2xl transform scale-105' 
                    : 'bg-white border border-gray-200'
                }`}
              >
                {plan.badge && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-yellow-400 text-gray-900 px-4 py-1 rounded-full text-sm font-semibold">
                      {plan.badge}
                    </span>
                  </div>
                )}
                
                {plan.discount && (
                  <div className="absolute -top-4 right-4">
                    <span className="bg-red-500 text-white px-3 py-1 rounded-full text-xs font-semibold">
                      {plan.discount}
                    </span>
                  </div>
                )}
                
                <div className="mb-8">
                  <h3 className={`text-2xl font-bold mb-2 ${plan.highlighted ? 'text-white' : 'text-gray-900'}`}>
                    {plan.name}
                  </h3>
                  <p className={`${plan.highlighted ? 'text-blue-100' : 'text-gray-600'}`}>
                    {plan.description}
                  </p>
                </div>
                
                <div className="mb-8">
                  <div className="flex items-baseline mb-2">
                    <span className={`text-5xl font-bold ${plan.highlighted ? 'text-white' : 'text-gray-900'}`}>
                      {plan.price}
                    </span>
                    <span className={`text-lg ml-2 ${plan.highlighted ? 'text-blue-100' : 'text-gray-600'}`}>
                      {plan.period}
                    </span>
                  </div>
                  {plan.originalPrice && (
                    <div className={`text-lg ${plan.highlighted ? 'text-blue-200' : 'text-gray-500'}`}>
                      <span className="line-through">{plan.originalPrice}</span>
                      <span className="ml-2 text-sm">regular price</span>
                    </div>
                  )}
                </div>
                
                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start">
                      <Check className={`w-5 h-5 mr-3 flex-shrink-0 ${
                        plan.highlighted ? 'text-blue-100' : 'text-green-500'
                      }`} />
                      <span className={plan.highlighted ? 'text-white' : 'text-gray-700'}>
                        {feature}
                      </span>
                    </li>
                  ))}
                </ul>
                
                <button
                  onClick={() => handleSubscribe(plan)}
                  className={`w-full py-3 rounded-lg font-semibold transition-all ${
                    plan.highlighted
                      ? 'bg-white text-blue-600 hover:bg-gray-100'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {plan.price === 'Custom' ? 'Contact Sales' : 'Reserve This Plan'}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Testimonials Section */}
      <div id="testimonials" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              What Beta Testers Are Saying
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Healthcare professionals who tested DiagnoAssist are already seeing the potential
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-gray-50 rounded-xl p-8">
                <div className="flex mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-gray-700 mb-6 italic">"{testimonial.content}"</p>
                <div>
                  <p className="font-semibold text-gray-900">{testimonial.name}</p>
                  <p className="text-gray-600">{testimonial.role}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* FAQ Section */}
      <div className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-xl text-gray-600">
              Everything you need to know about the early access program
            </p>
          </div>
          
          <div className="space-y-6">
            {faqs.map((faq, index) => (
              <div key={index} className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {faq.question}
                </h3>
                <p className="text-gray-600">
                  {faq.answer}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* CTA Section */}
      <div className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center px-8">
          <h2 className="text-4xl font-bold text-white mb-6">
            Don't Miss Out on Early Bird Pricing!
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join 500+ forward-thinking healthcare professionals who are ready to revolutionize patient care.
          </p>
          <button 
            onClick={() => handleSubscribe(plans[1])}
            className="px-10 py-4 bg-white text-blue-600 text-lg font-semibold rounded-xl hover:bg-gray-100 transition-all transform hover:scale-105 shadow-xl"
          >
            Reserve Your Spot Today
          </button>
          <p className="text-sm text-blue-200 mt-4">
            No credit card required • Cancel anytime before launch
          </p>
        </div>
      </div>
      
      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="max-w-7xl mx-auto px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
                  <Activity className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold text-white">DiagnoAssist</span>
              </div>
              <p className="text-gray-400">
                AI-powered diagnostic assistant for modern healthcare
              </p>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2">
                <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Security</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Legal</h4>
              <ul className="space-y-2">
                <li><a href="#" className="hover:text-white transition-colors">Privacy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms</a></li>
                <li><a href="#" className="hover:text-white transition-colors">HIPAA</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Compliance</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 pt-8 text-center">
            <p>&copy; 2024 DiagnoAssist. All rights reserved.</p>
          </div>
        </div>
      </footer>
      
      {/* Subscription Modal */}
      {showSubscriptionModal && (
        <SubscriptionModal 
          plan={selectedPlan} 
          onClose={() => setShowSubscriptionModal(false)} 
        />
      )}
      
      {/* Demo Disclaimer Modal */}
      {showDemoDisclaimer && (
        <DemoDisclaimer 
          onClose={() => setShowDemoDisclaimer(false)} 
        />
      )}
      
      {/* Countdown Timer */}
      <CountdownTimer />
    </>
  );
};

export default LandingPage;