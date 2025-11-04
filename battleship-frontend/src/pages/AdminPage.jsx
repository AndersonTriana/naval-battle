import { useState } from 'react';
import FleetManagement from '../components/Admin/FleetManagement';
import ShipTemplateManagement from '../components/Admin/ShipTemplateManagement';

const AdminPage = () => {
  const [activeTab, setActiveTab] = useState('templates'); // 'templates' | 'fleets'

  const tabs = [
    { id: 'templates', label: '🚢 Plantillas de Barcos', component: ShipTemplateManagement },
    { id: 'fleets', label: '⚓ Flotas', component: FleetManagement },
  ];

  const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">
          🛠️ Panel de Administración
        </h1>
        <p className="text-gray-400">
          Gestiona plantillas de barcos y flotas base del sistema
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-700">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-indigo-500 text-indigo-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div>
        {ActiveComponent && <ActiveComponent />}
      </div>
    </div>
  );
};

export default AdminPage;
