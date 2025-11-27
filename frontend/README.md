# Frontend Architecture and How It Works

### **Core Technologies**

The frontend is a modern web application built with:
*   **React:** A library for building user interfaces with a component-based architecture.
*   **TypeScript:** Adds static typing to JavaScript, which helps prevent bugs and improves code quality.
*   **Vite:** A fast and modern build tool that provides a great development experience with features like instant server start and hot module replacement.
*   **Material-UI (MUI):** A comprehensive library of pre-built React components that implement Google's Material Design. This was used to create the professional, "mission control" look and feel.
*   **Leaflet & React-Leaflet:** A popular open-source library for creating interactive maps, used to display the locations of road defects.
*   **Axios:** A library for making HTTP requests, used to fetch data from our backend server.

---

### **Project Structure and Key Files**

The main logic resides in the `frontend/src` directory:

```
frontend/
└── src/
    ├── components/         // Reusable UI components
    │   ├── AnalyticsWidgets.tsx
    │   ├── DashboardLayout.tsx
    │   ├── DefectTable.tsx
    │   └── Roadmap.tsx
    ├── context/            // For global state management
    │   └── DefectsContext.tsx
    ├── App.tsx             // The main application component
    └── main.tsx            // The entry point of the application
```

---

### **How It Works: From Data to Display**

The application follows a clear, modern data flow pattern:

**1. The Entry Point (`main.tsx`)**
*   This is the very first file that runs.
*   It finds the `<div id="root">` in `index.html` and tells React to render our application inside it.
*   Crucially, it wraps our entire application with Material-UI's `ThemeProvider` and injects a dark theme. This ensures every component we build has a consistent, professional dark mode look.

**2. State Management (`context/DefectsContext.tsx`)**
*   To avoid having to pass data down through many layers of components, we use React's Context API for global state management.
*   `DefectsContext` is the heart of our data handling. When the application loads, the `DefectsProvider` in this file automatically makes a call to the backend API (`http://localhost:8000/data`) using `axios`.
*   It then stores the fetched defect data, along with loading and error states, in a central location.

**3. The Main App Component (`App.tsx`)**
*   This component orchestrates the overall layout.
*   It wraps all the visible components with the `DefectsProvider`. This makes the defect data available to any component that needs it.
*   It uses a custom hook, `useDefects()`, to check the `loading` and `error` states from the context. It will show a loading spinner while data is being fetched or an error message if the backend isn't running, which is very user-friendly.

**4. The UI Components (`components/`)**
*   **`DashboardLayout.tsx`**: Provides the main structure, including the top `AppBar` with the title and the dark background for the main content area.
*   **`AnalyticsWidgets.tsx`**, **`Roadmap.tsx`**, and **`DefectTable.tsx`**: Each of these components also uses the `useDefects()` hook to get access to the shared defect data.
    *   The **Analytics** component calculates statistics (total defects, defects today) from the data.
    *   The **Roadmap** component loops through the defects and renders a `Marker` on the map for each one.
    *   The **Defect Table** loops through the defects and renders a row in the table for each one.

This architecture is powerful because it decouples the components from each other. The `Roadmap` doesn't need to know anything about the `DefectTable`. Both simply ask the `DefectsContext` for the data they need, making the system easy to manage and extend.

---

### **How to Run It**

1.  **Run the Backend:** In one terminal, from the root directory (`D:\Hackathon\Ideathon 25`), run `uvicorn backend.app:app --reload`.
2.  **Run the Frontend:** In a second terminal, navigate to the frontend directory (`cd frontend`) and run `npm run dev`.

The frontend will start, fetch data from the running backend, and display the full dashboard in your browser.