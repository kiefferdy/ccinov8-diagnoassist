interface StepNavigationProps {
  steps: string[];
  current: number;
}

export default function StepNavigation({ steps, current }: StepNavigationProps) {
  return (
    <ol className="flex space-x-2 mb-4">
      {steps.map((step, index) => (
        <li key={index} className={`flex-1 px-2 py-1 text-center rounded-full text-sm ${index === current ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>{step}</li>
      ))}
    </ol>
  );
}
