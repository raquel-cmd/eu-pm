import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTemplates, useSeedTemplates } from '../hooks/useTemplates';
import {
  TemplateCategory,
  TEMPLATE_CATEGORY_LABELS,
  PERSONNEL_TEMPLATE_TYPE_LABELS,
} from '../types';
import type { DocumentTemplate } from '../types';

function TemplateCategoryBadge({ category }: { category: TemplateCategory }) {
  const colors: Record<TemplateCategory, string> = {
    [TemplateCategory.PERSONNEL]: 'bg-blue-100 text-blue-800',
    [TemplateCategory.EC_CONSORTIUM]: 'bg-purple-100 text-purple-800',
    [TemplateCategory.REPORTING]: 'bg-green-100 text-green-800',
    [TemplateCategory.MISSION_TRAVEL]: 'bg-amber-100 text-amber-800',
    [TemplateCategory.PROCUREMENT]: 'bg-red-100 text-red-800',
  };
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[category]}`}
    >
      {TEMPLATE_CATEGORY_LABELS[category]}
    </span>
  );
}

function TemplateCard({
  template,
  onSelect,
}: {
  template: DocumentTemplate;
  onSelect: (t: DocumentTemplate) => void;
}) {
  return (
    <div
      className="bg-white border border-gray-200 rounded-lg p-5 hover:shadow-md
        transition-shadow cursor-pointer"
      onClick={() => onSelect(template)}
    >
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-900">{template.name}</h3>
        <TemplateCategoryBadge category={template.category} />
      </div>
      {template.description && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {template.description}
        </p>
      )}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>
          {template.personnel_type
            ? PERSONNEL_TEMPLATE_TYPE_LABELS[template.personnel_type]
            : template.slug}
        </span>
        <span>v{template.version}</span>
      </div>
    </div>
  );
}

export default function TemplateLibraryPage() {
  const navigate = useNavigate();
  const [categoryFilter, setCategoryFilter] = useState<TemplateCategory | ''>('');
  const { data: templates, isLoading, error } = useTemplates(
    categoryFilter || undefined,
  );
  const seedMutation = useSeedTemplates();

  function handleSelect(template: DocumentTemplate) {
    navigate(`/templates/${template.id}/fill`);
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Template Library</h1>
          <p className="text-sm text-gray-600 mt-1">
            Browse and generate documents from templates
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => seedMutation.mutate()}
            disabled={seedMutation.isPending}
            className="inline-flex items-center px-4 py-2 border border-gray-300
              rounded-md text-sm font-medium text-gray-700 bg-white
              hover:bg-gray-50 disabled:opacity-50"
          >
            {seedMutation.isPending ? 'Seeding...' : 'Seed Templates'}
          </button>
          <Link
            to="/templates/documents"
            className="inline-flex items-center px-4 py-2 border border-gray-300
              rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Generated Documents
          </Link>
        </div>
      </div>

      {/* Category filter */}
      <div className="mb-6">
        <div className="flex gap-2">
          <button
            onClick={() => setCategoryFilter('')}
            className={`px-3 py-1.5 rounded-full text-sm font-medium ${
              !categoryFilter
                ? 'bg-blue-700 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            All
          </button>
          {Object.values(TemplateCategory).map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium ${
                categoryFilter === cat
                  ? 'bg-blue-700 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {TEMPLATE_CATEGORY_LABELS[cat]}
            </button>
          ))}
        </div>
      </div>

      {seedMutation.isSuccess && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md text-sm text-green-800">
          Templates seeded successfully.
        </div>
      )}

      {isLoading && (
        <div className="text-center py-12 text-gray-500">Loading templates...</div>
      )}

      {error && (
        <div className="text-center py-12 text-red-600">
          Failed to load templates. Make sure to seed templates first.
        </div>
      )}

      {templates && templates.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">No templates found.</p>
          <button
            onClick={() => seedMutation.mutate()}
            className="text-blue-700 hover:underline text-sm"
          >
            Seed built-in templates
          </button>
        </div>
      )}

      {templates && templates.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((t) => (
            <TemplateCard key={t.id} template={t} onSelect={handleSelect} />
          ))}
        </div>
      )}
    </div>
  );
}
