/**
 * File: ReportViewer.tsx
 * 
 * Overview:
 * Interactive report viewer component with markdown rendering and export options.
 * 
 * Purpose:
 * Displays generated reports with navigation, search, and export capabilities.
 * 
 * Dependencies:
 * - react-markdown: Markdown rendering
 * - react-syntax-highlighter: Code highlighting
 * - downloadjs: File downloads
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import {
  DocumentTextIcon,
  DownloadIcon,
  PrinterIcon,
  ShareIcon,
  BookOpenIcon,
  SearchIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ZoomInIcon,
  ZoomOutIcon,
  ClipboardCopyIcon,
  CheckIcon,
  MenuIcon,
  XIcon
} from '@heroicons/react/outline';

interface ReportViewerProps {
  reportContent: string;
  reportTitle: string;
  reportId?: string;
  metadata?: any;
  visualizations?: Array<{
    title: string;
    filename: string;
    type: string;
  }>;
  onExport?: (format: string) => void;
  onShare?: () => void;
  onEdit?: () => void;
}

interface TableOfContentsItem {
  id: string;
  title: string;
  level: number;
}

const ReportViewer: React.FC<ReportViewerProps> = ({
  reportContent,
  reportTitle,
  reportId,
  metadata,
  visualizations = [],
  onExport,
  onShare,
  onEdit
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [highlightedContent, setHighlightedContent] = useState(reportContent);
  const [tableOfContents, setTableOfContents] = useState<TableOfContentsItem[]>([]);
  const [currentSection, setCurrentSection] = useState('');
  const [fontSize, setFontSize] = useState(16);
  const [showSidebar, setShowSidebar] = useState(true);
  const [copied, setCopied] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  // Generate table of contents from markdown headers
  useEffect(() => {
    const headers = reportContent.match(/^#{1,3}\s+.+$/gm) || [];
    const toc = headers.map((header, index) => {
      const level = header.match(/^#+/)?.[0].length || 1;
      const title = header.replace(/^#+\s+/, '');
      const id = `section-${index}`;
      return { id, title, level };
    });
    setTableOfContents(toc);
  }, [reportContent]);

  // Highlight search results
  useEffect(() => {
    if (!searchQuery) {
      setHighlightedContent(reportContent);
      return;
    }

    const regex = new RegExp(`(${searchQuery})`, 'gi');
    const highlighted = reportContent.replace(regex, '<mark>$1</mark>');
    setHighlightedContent(highlighted);
  }, [searchQuery, reportContent]);

  // Handle export
  const handleExport = (format: string) => {
    if (onExport) {
      onExport(format);
    } else {
      // Default export implementation
      const blob = new Blob([reportContent], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${reportTitle.replace(/\s+/g, '_')}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  // Handle print
  const handlePrint = () => {
    window.print();
  };

  // Handle copy to clipboard
  const handleCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(reportContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Scroll to section
  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
      setCurrentSection(sectionId);
    }
  };

  // Custom renderers for markdown
  const markdownComponents = {
    code({ node, inline, className, children, ...props }: any) {
      const match = /language-(\w+)/.exec(className || '');
      return !inline && match ? (
        <SyntaxHighlighter
          style={vscDarkPlus}
          language={match[1]}
          PreTag="div"
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      ) : (
        <code className={className} {...props}>
          {children}
        </code>
      );
    },
    h1: ({ children, ...props }: any) => {
      const index = tableOfContents.findIndex(item => item.title === String(children));
      const id = index >= 0 ? tableOfContents[index].id : '';
      return <h1 id={id} className="text-3xl font-bold mt-8 mb-4" {...props}>{children}</h1>;
    },
    h2: ({ children, ...props }: any) => {
      const index = tableOfContents.findIndex(item => item.title === String(children));
      const id = index >= 0 ? tableOfContents[index].id : '';
      return <h2 id={id} className="text-2xl font-semibold mt-6 mb-3" {...props}>{children}</h2>;
    },
    h3: ({ children, ...props }: any) => {
      const index = tableOfContents.findIndex(item => item.title === String(children));
      const id = index >= 0 ? tableOfContents[index].id : '';
      return <h3 id={id} className="text-xl font-medium mt-4 mb-2" {...props}>{children}</h3>;
    },
    table: ({ children, ...props }: any) => (
      <div className="overflow-x-auto my-4">
        <table className="min-w-full divide-y divide-gray-200" {...props}>
          {children}
        </table>
      </div>
    ),
    thead: ({ children, ...props }: any) => (
      <thead className="bg-gray-50" {...props}>{children}</thead>
    ),
    tbody: ({ children, ...props }: any) => (
      <tbody className="bg-white divide-y divide-gray-200" {...props}>{children}</tbody>
    ),
    th: ({ children, ...props }: any) => (
      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider" {...props}>
        {children}
      </th>
    ),
    td: ({ children, ...props }: any) => (
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900" {...props}>
        {children}
      </td>
    ),
  };

  return (
    <div className="flex h-full bg-gray-50">
      {/* Sidebar - Table of Contents */}
      {showSidebar && (
        <div className="w-64 bg-white border-r border-gray-200 overflow-y-auto">
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-4">Table of Contents</h3>
            <nav className="space-y-1">
              {tableOfContents.map((item) => (
                <button
                  key={item.id}
                  onClick={() => scrollToSection(item.id)}
                  className={`
                    block w-full text-left px-3 py-2 rounded-md text-sm
                    ${currentSection === item.id ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50'}
                    ${item.level === 1 ? 'font-semibold' : ''}
                    ${item.level === 2 ? 'pl-6' : ''}
                    ${item.level === 3 ? 'pl-9' : ''}
                  `}
                  style={{ paddingLeft: `${item.level * 12}px` }}
                >
                  {item.title}
                </button>
              ))}
            </nav>
          </div>

          {/* Visualizations */}
          {visualizations.length > 0 && (
            <div className="p-4 border-t border-gray-200">
              <h3 className="text-lg font-semibold mb-4">Visualizations</h3>
              <div className="space-y-2">
                {visualizations.map((viz, index) => (
                  <div
                    key={index}
                    className="flex items-center p-2 rounded-md hover:bg-gray-50 cursor-pointer"
                  >
                    <DocumentTextIcon className="h-5 w-5 text-gray-400 mr-2" />
                    <span className="text-sm text-gray-700">{viz.title}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <div className="bg-white border-b border-gray-200 px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowSidebar(!showSidebar)}
                className="p-2 rounded-md hover:bg-gray-100"
              >
                {showSidebar ? <XIcon className="h-5 w-5" /> : <MenuIcon className="h-5 w-5" />}
              </button>
              
              <h1 className="text-xl font-semibold">{reportTitle}</h1>
              
              {reportId && (
                <span className="text-sm text-gray-500">ID: {reportId}</span>
              )}
            </div>

            <div className="flex items-center space-x-2">
              {/* Search */}
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-8 pr-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <SearchIcon className="absolute left-2 top-1.5 h-4 w-4 text-gray-400" />
              </div>

              {/* Font size controls */}
              <button
                onClick={() => setFontSize(Math.max(12, fontSize - 2))}
                className="p-2 rounded-md hover:bg-gray-100"
                title="Decrease font size"
              >
                <ZoomOutIcon className="h-5 w-5" />
              </button>
              <button
                onClick={() => setFontSize(Math.min(24, fontSize + 2))}
                className="p-2 rounded-md hover:bg-gray-100"
                title="Increase font size"
              >
                <ZoomInIcon className="h-5 w-5" />
              </button>

              {/* Action buttons */}
              <div className="flex items-center space-x-1 pl-2 border-l border-gray-200">
                <button
                  onClick={() => handleCopyToClipboard()}
                  className="p-2 rounded-md hover:bg-gray-100"
                  title="Copy to clipboard"
                >
                  {copied ? (
                    <CheckIcon className="h-5 w-5 text-green-500" />
                  ) : (
                    <ClipboardCopyIcon className="h-5 w-5" />
                  )}
                </button>
                
                <button
                  onClick={handlePrint}
                  className="p-2 rounded-md hover:bg-gray-100"
                  title="Print"
                >
                  <PrinterIcon className="h-5 w-5" />
                </button>

                {onShare && (
                  <button
                    onClick={onShare}
                    className="p-2 rounded-md hover:bg-gray-100"
                    title="Share"
                  >
                    <ShareIcon className="h-5 w-5" />
                  </button>
                )}

                {onEdit && (
                  <button
                    onClick={onEdit}
                    className="p-2 rounded-md hover:bg-gray-100"
                    title="Edit"
                  >
                    <BookOpenIcon className="h-5 w-5" />
                  </button>
                )}

                {/* Export dropdown */}
                <div className="relative group">
                  <button
                    className="p-2 rounded-md hover:bg-gray-100"
                    title="Export"
                  >
                    <DownloadIcon className="h-5 w-5" />
                  </button>
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10">
                    <div className="py-1">
                      <button
                        onClick={() => handleExport('md')}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        Export as Markdown
                      </button>
                      <button
                        onClick={() => handleExport('html')}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        Export as HTML
                      </button>
                      <button
                        onClick={() => handleExport('pdf')}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        Export as PDF
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Report Content */}
        <div
          ref={contentRef}
          className="flex-1 overflow-y-auto p-8 bg-white"
          style={{ fontSize: `${fontSize}px` }}
        >
          <div className="max-w-4xl mx-auto">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={markdownComponents}
            >
              {highlightedContent}
            </ReactMarkdown>

            {/* Metadata section */}
            {metadata && (
              <div className="mt-8 p-4 bg-gray-50 rounded-lg">
                <h3 className="text-lg font-semibold mb-2">Report Metadata</h3>
                <dl className="grid grid-cols-2 gap-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Generated</dt>
                    <dd className="text-sm text-gray-900">{metadata.generated_at}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Sections</dt>
                    <dd className="text-sm text-gray-900">{metadata.sections?.length || 0}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Visualizations</dt>
                    <dd className="text-sm text-gray-900">{visualizations.length}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Report ID</dt>
                    <dd className="text-sm text-gray-900 font-mono">{reportId || 'N/A'}</dd>
                  </div>
                </dl>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportViewer;