import React, { useState } from 'react';
import { X, CreditCard, Lock, Check } from 'lucide-react';

const SubscriptionModal = ({ plan, onClose }) => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    cardNumber: '',
    expiry: '',
    cvv: '',
    zipCode: ''
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    // Format card number
    if (name === 'cardNumber') {
      const formatted = value.replace(/\s/g, '').match(/.{1,4}/g)?.join(' ') || value;
      setFormData({ ...formData, [name]: formatted });
    }
    // Format expiry
    else if (name === 'expiry') {
      const formatted = value.replace(/\D/g, '').replace(/(\d{2})(\d)/, '$1/$2').substr(0, 5);
      setFormData({ ...formData, [name]: formatted });
    }
    // Limit CVV to 3 digits
    else if (name === 'cvv') {
      setFormData({ ...formData, [name]: value.slice(0, 3) });
    }
    else {
      setFormData({ ...formData, [name]: value });
    }
  };
  
  const handleNext = () => {
    if (step === 1) {
      // Validate email and name
      if (formData.email && formData.name) {
        setStep(2);
      }
    } else if (step === 2) {
      // Validate payment info
      if (formData.cardNumber && formData.expiry && formData.cvv && formData.zipCode) {
        processPayment();
      }
    }
  };
  
  const processPayment = async () => {
    setIsProcessing(true);
    // Simulate payment processing
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsProcessing(false);
    setIsComplete(true);
    // Auto close after 3 seconds
    setTimeout(() => {
      onClose();
    }, 3000);
  };
  
  if (isComplete) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4">
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Check className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Welcome to DiagnoAssist Early Access!</h3>
            <p className="text-gray-600 mb-4">
              Your reservation for the {plan?.name} plan has been confirmed.
            </p>
            <p className="text-sm text-gray-500">
              You'll receive a confirmation email with launch updates and your exclusive pricing details.
            </p>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            Reserve {plan?.name} Plan - Early Bird Special
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        
        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-8">
          <div className="flex items-center">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
              step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-400'
            }`}>
              1
            </div>
            <div className={`w-20 h-1 ${step >= 2 ? 'bg-blue-600' : 'bg-gray-200'}`} />
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
              step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-400'
            }`}>
              2
            </div>
          </div>
        </div>
        
        {/* Step 1: Account Information */}
        {/* {step === 1 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Account Information</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="doctor@example.com"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Dr. Jane Smith"
                  required
                />
              </div>
            </div>
          </div>
        )} */}
        
        {/* Step 2: Payment Information */}
        {step === 2 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Payment Information</h3>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <div className="flex items-center">
                <Lock className="w-5 h-5 text-blue-600 mr-2" />
                <p className="text-sm text-blue-800">
                  This is a reservation only - no charges will be made until DiagnoAssist launches in Q3 2025
                </p>
              </div>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Card Number
                </label>
                <div className="relative">
                  <input
                    type="text"
                    name="cardNumber"
                    value={formData.cardNumber}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="1234 5678 9012 3456"
                    maxLength="19"
                    required
                  />
                  <CreditCard className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Expiry Date
                  </label>
                  <input
                    type="text"
                    name="expiry"
                    value={formData.expiry}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="MM/YY"
                    maxLength="5"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    CVV
                  </label>
                  <input
                    type="text"
                    name="cvv"
                    value={formData.cvv}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="123"
                    maxLength="3"
                    required
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  ZIP Code
                </label>
                <input
                  type="text"
                  name="zipCode"
                  value={formData.zipCode}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="12345"
                  required
                />
              </div>
            </div>
          </div>
        )}
        
        {/* Plan Summary */}
        <div className="bg-gray-50 rounded-lg p-6 mb-6 mt-8">
          <h4 className="font-semibold text-gray-900 mb-3">Reservation Summary</h4>
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-600">{plan?.name} Plan (Early Bird)</span>
            <span className="font-semibold text-gray-900">{plan?.price}/month</span>
          </div>
          {plan?.originalPrice && (
            <div className="flex justify-between items-center mb-2">
              <span className="text-gray-600">Regular Price</span>
              <span className="text-gray-500 line-through">{plan?.originalPrice}/month</span>
            </div>
          )}
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-600">Your Savings</span>
            <span className="text-green-600 font-medium">{plan?.discount}</span>
          </div>
          <div className="border-t pt-2 mt-2">
            <div className="flex justify-between items-center">
              <span className="font-semibold text-gray-900">Due Today</span>
              <span className="font-bold text-xl text-gray-900">₱0.00</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">You'll be charged when DiagnoAssist launches</p>
          </div>
        </div>
        
        {/* Action Buttons */}
        <div className="w-full flex justify-around">
         <button
               onClick={() => (window.location.href = 'https://forms.gle/iFwZQRzV2WL3ap2s8')}
              className='px-6 py-2 w-full bg-blue-600 text-white hover:bg-blue-700 rounded-md'
            >Reserve now</button>
          </div>
        {/* <div className="flex justify-between">
          {step > 1 && (
            <button
              onClick={() => setStep(step - 1)}
              className="px-6 py-2 text-gray-600 hover:text-gray-900 transition-colors"
              disabled={isProcessing}
            >
              Back
            </button>
          )}
          <button
            onClick={handleNext}
            disabled={isProcessing || 
              (step === 1 && (!formData.email || !formData.name)) ||
              (step === 2 && (!formData.cardNumber || !formData.expiry || !formData.cvv || !formData.zipCode))
            }
            className={`ml-auto px-8 py-3 rounded-lg font-medium transition-all ${
              isProcessing || 
              (step === 1 && (!formData.email || !formData.name)) ||
              (step === 2 && (!formData.cardNumber || !formData.expiry || !formData.cvv || !formData.zipCode))
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isProcessing ? (
              <span className="flex items-center">
                <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Processing...
              </span>
            ) : step === 1 ? 'Continue to Payment' : 'Complete Reservation'}
          </button>
        </div> */}
      </div>
    </div>
  );
};

export default SubscriptionModal;