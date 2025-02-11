import React from 'react';
import { Navbar } from '../components/Landing/Navbar';
import { Check } from 'lucide-react';
import { Link } from 'react-router-dom';
import { theme } from '../styles/themes';

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
    <div className={`min-h-screen bg-gradient-to-b ${theme.colors.background.main} relative overflow-hidden`}>
      <Navbar />
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className={`absolute top-0 -right-1/4 w-[600px] h-[600px] rounded-full bg-gradient-to-br ${theme.colors.background.glow.primary} blur-3xl animate-pulse`}></div>
        <div className={`absolute bottom-0 -left-1/4 w-[600px] h-[600px] rounded-full bg-gradient-to-tl ${theme.colors.background.glow.secondary} blur-3xl animate-pulse`} style={{ animationDuration: '8s' }}></div>
      </div>
      <div className="pt-20 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className={`text-4xl font-bold mb-4 ${theme.colors.primary.text.dark}`}>Simple, Transparent Pricing</h1>
            <p className="text-xl text-gray-600 dark:text-gray-300">Choose the plan that's right for you</p>
          </div>
          <div className="mt-16 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {plans.map((plan) => (
              <div key={plan.name} className={`relative overflow-hidden rounded-lg shadow-lg ${theme.colors.card.gradient} backdrop-blur-sm p-8 ${plan.popular ? `ring-2 ${theme.colors.primary.border}` : ''}`}>
                {plan.popular && (
                  <div className="absolute top-0 right-0">
                    <div className={`text-xs ${theme.colors.primary.button.bg} text-white px-3 py-1 rounded-bl-lg`}>
                      Popular
                    </div>
                  </div>
                )}
                <h3 className={`text-2xl font-bold mb-4 ${theme.colors.primary.text.dark}`}>{plan.name}</h3>
                <p className={`text-4xl font-bold mb-6 ${theme.colors.primary.text.dark}`}>{plan.price}<span className="text-gray-500 text-base font-normal">{plan.price !== "Custom" ? "/month" : ""}</span></p>
                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center">
                      <Check className={`h-5 w-5 ${theme.colors.primary.solid} mr-2`} />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  to="/signup"
                  className={`block w-full text-center rounded-lg px-4 py-2 font-medium transition-all duration-300 ${
                    plan.popular
                      ? `${theme.colors.primary.button.bg} ${theme.colors.primary.button.hover} text-white`
                      : 'bg-gradient-to-r from-gray-100 to-gray-200 text-gray-900 hover:from-gray-200 hover:to-gray-300 dark:from-gray-700 dark:to-gray-800 dark:text-white dark:hover:from-gray-600 dark:hover:to-gray-700'
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
