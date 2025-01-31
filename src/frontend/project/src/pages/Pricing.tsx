import React from 'react';
import { Navbar } from '../components/Landing/Navbar';
import { Check } from 'lucide-react';
import { Link } from 'react-router-dom';

const Pricing: React.FC = () => {
  const plans = [
    {
      name: "Free",
      price: "$0",
      features: [
        "Convert up to 10 threads per month",
        "Basic AI formatting",
        "Twitter integration",
        "Export to Markdown"
      ]
    },
    {
      name: "Pro",
      price: "$19",
      popular: true,
      features: [
        "Unlimited thread conversions",
        "Advanced AI formatting",
        "Priority support",
        "Custom templates",
        "Analytics dashboard",
        "Multi-platform publishing"
      ]
    },
    {
      name: "Enterprise",
      price: "Custom",
      features: [
        "Everything in Pro",
        "Custom AI training",
        "API access",
        "Dedicated support",
        "Custom integrations",
        "Team collaboration"
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <div className="pt-20 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-4">Simple, Transparent Pricing</h1>
            <p className="text-xl text-gray-600 dark:text-gray-300">Choose the plan that's right for you</p>
          </div>
          <div className="mt-16 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {plans.map((plan) => (
              <div key={plan.name} className={`rounded-lg shadow-lg bg-white dark:bg-gray-800 p-8 ${plan.popular ? 'ring-2 ring-blue-500' : ''}`}>
                <h3 className="text-2xl font-bold mb-4">{plan.name}</h3>
                <p className="text-4xl font-bold mb-6">{plan.price}<span className="text-gray-500 text-base font-normal">{plan.price !== "Custom" ? "/month" : ""}</span></p>
                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center">
                      <Check className="h-5 w-5 text-green-500 mr-2" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  to="/signup"
                  className={`block w-full text-center rounded-lg px-4 py-2 font-medium ${
                    plan.popular
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600'
                  }`}
                >
                  Get Started
                </Link>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Pricing;
