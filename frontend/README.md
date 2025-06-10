# DiagnoAssist Frontend

The React-based frontend for the DiagnoAssist medical diagnosis assistant.

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and navigate to `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Tech Stack

- **React** - UI framework
- **Tailwind CSS** - Styling
- **React Router DOM** - Navigation
- **React Hook Form** - Form management
- **Lucide React** - Icons
- **Vite** - Build tool

## Project Structure

```
src/
├── components/
│   ├── Layout/          # Main layout with sidebar
│   ├── Home/           # Landing page
│   ├── Patient/        # Patient info & clinical assessment
│   ├── Diagnosis/      # Physical exam & diagnostic analysis
│   ├── Tests/          # Test management
│   └── Treatment/      # Final diagnosis & treatment
├── contexts/           # React contexts (PatientContext)
├── App.jsx            # Main app component
└── main.jsx           # Entry point
```
