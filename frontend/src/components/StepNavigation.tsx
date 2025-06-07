interface StepNavigationProps {
  steps: string[];
  current: number;
}

export default function StepNavigation({ steps, current }: StepNavigationProps) {
  return (
    <ol className="flex items-center mb-6">
      {steps.map((step, index) => (
        <li key={step} className="flex items-center w-full">
          <div
            className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
              index <= current ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
            }`}
          >
            {index + 1}
          </div>
          <span
            className={`ml-2 text-sm sm:text-base ${
              index === current ? 'text-blue-600 font-semibold' : 'text-gray-600'
            }`}
          >
            {step}
          </span>
          {index < steps.length - 1 && (
            <div className="flex-1 h-px bg-gray-300 mx-2" />
          )}
        </li>
      ))}
    </ol>
  );
}
