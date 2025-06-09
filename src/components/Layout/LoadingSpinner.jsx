import clsx from 'clsx'

const LoadingSpinner = ({ size = 'medium', className = '', text = '' }) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  }

  return (
    <div className={clsx('flex flex-col items-center justify-center', className)}>
      <div 
        className={clsx(
          'animate-spin rounded-full border-2 border-gray-200 border-t-primary-600',
          sizeClasses[size]
        )}
      ></div>
      {text && (
        <p className="mt-2 text-sm text-gray-600">{text}</p>
      )}
    </div>
  )
}

export default LoadingSpinner