import React, { useState, useEffect } from 'react';
import '@/App.css';
import TranspilerWorkspace from './components/TranspilerWorkspace';
import { Toaster } from '@/components/ui/sonner';

function App() {
  return (
    <div className="App h-screen w-full overflow-hidden bg-background text-foreground">
      <TranspilerWorkspace />
      <Toaster />
    </div>
  );
}

export default App;