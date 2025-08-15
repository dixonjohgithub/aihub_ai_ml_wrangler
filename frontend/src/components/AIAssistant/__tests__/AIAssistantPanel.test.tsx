/**
 * Test suite for AI Assistant Panel components
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import AIAssistantPanel from '../AIAssistantPanel';
import { useAIAssistant } from '../../../hooks/useAIAssistant';
import { AnalysisType, SuggestionPriority } from '../../../types/ai';

// Mock the useAIAssistant hook
vi.mock('../../../hooks/useAIAssistant');

describe('AIAssistantPanel', () => {
  const mockAnalyzeDataset = vi.fn();
  const mockSubmitFeedback = vi.fn();
  const mockClearError = vi.fn();
  const mockOnClose = vi.fn();
  const mockOnSuggestionApply = vi.fn();

  const mockSuggestions = [
    {
      id: '1',
      type: 'general',
      title: 'Test Suggestion',
      description: 'Test description',
      rationale: 'Test rationale',
      priority: SuggestionPriority.HIGH,
      impactScore: 0.8,
      confidenceScore: 0.9,
      implementationCode: 'print("test")',
      affectedColumns: ['col1', 'col2']
    }
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    (useAIAssistant as any).mockReturnValue({
      suggestions: mockSuggestions,
      isLoading: false,
      error: null,
      history: [],
      analyzeDataset: mockAnalyzeDataset,
      submitFeedback: mockSubmitFeedback,
      clearError: mockClearError
    });
  });

  it('renders when open', () => {
    render(
      <AIAssistantPanel
        isOpen={true}
        onClose={mockOnClose}
        onSuggestionApply={mockOnSuggestionApply}
      />
    );

    expect(screen.getByText('AI Assistant')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(
      <AIAssistantPanel
        isOpen={false}
        onClose={mockOnClose}
        onSuggestionApply={mockOnSuggestionApply}
      />
    );

    expect(screen.queryByText('AI Assistant')).not.toBeInTheDocument();
  });

  it('switches between tabs', () => {
    render(
      <AIAssistantPanel
        isOpen={true}
        onClose={mockOnClose}
        onSuggestionApply={mockOnSuggestionApply}
      />
    );

    // Click on Chat tab
    fireEvent.click(screen.getByText('Chat'));
    expect(screen.getByPlaceholderText('Ask me about your data...')).toBeInTheDocument();

    // Click on History tab
    fireEvent.click(screen.getByText('History'));
    expect(screen.getByText('No Analysis History')).toBeInTheDocument();

    // Click back on Suggestions tab
    fireEvent.click(screen.getByText('Suggestions'));
    expect(screen.getByText('Test Suggestion')).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    render(
      <AIAssistantPanel
        isOpen={true}
        onClose={mockOnClose}
        onSuggestionApply={mockOnSuggestionApply}
      />
    );

    const closeButton = screen.getByTitle('Close');
    fireEvent.click(closeButton);
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('displays error message when error exists', () => {
    (useAIAssistant as any).mockReturnValue({
      suggestions: [],
      isLoading: false,
      error: 'Test error message',
      history: [],
      analyzeDataset: mockAnalyzeDataset,
      submitFeedback: mockSubmitFeedback,
      clearError: mockClearError
    });

    render(
      <AIAssistantPanel
        isOpen={true}
        onClose={mockOnClose}
        onSuggestionApply={mockOnSuggestionApply}
      />
    );

    expect(screen.getByText('Test error message')).toBeInTheDocument();
  });

  it('analyzes dataset when opened with data', async () => {
    const dataset = { col1: [1, 2, 3], col2: ['a', 'b', 'c'] };

    render(
      <AIAssistantPanel
        isOpen={true}
        onClose={mockOnClose}
        dataset={dataset}
        onSuggestionApply={mockOnSuggestionApply}
      />
    );

    await waitFor(() => {
      expect(mockAnalyzeDataset).toHaveBeenCalledWith(dataset, AnalysisType.GENERAL);
    });
  });

  it('toggles panel expansion', () => {
    render(
      <AIAssistantPanel
        isOpen={true}
        onClose={mockOnClose}
        onSuggestionApply={mockOnSuggestionApply}
      />
    );

    const expandButton = screen.getByTitle('Expand');
    fireEvent.click(expandButton);
    
    // After expansion, the button should change to collapse
    expect(screen.getByTitle('Collapse')).toBeInTheDocument();
  });
});

describe('SuggestionCards', () => {
  it('displays suggestions correctly', () => {
    const SuggestionCards = require('../SuggestionCards').default;
    
    const suggestions = [
      {
        id: '1',
        type: 'general',
        title: 'Impute Missing Values',
        description: 'Handle missing data in numeric columns',
        rationale: 'Improves model performance',
        priority: SuggestionPriority.HIGH,
        impactScore: 0.8,
        confidenceScore: 0.9,
        affectedColumns: ['age', 'salary']
      }
    ];

    render(
      <SuggestionCards
        suggestions={suggestions}
        onApply={vi.fn()}
        onFeedback={vi.fn()}
        isLoading={false}
      />
    );

    expect(screen.getByText('Impute Missing Values')).toBeInTheDocument();
    expect(screen.getByText('Handle missing data in numeric columns')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    const SuggestionCards = require('../SuggestionCards').default;
    
    render(
      <SuggestionCards
        suggestions={[]}
        onApply={vi.fn()}
        onFeedback={vi.fn()}
        isLoading={true}
      />
    );

    expect(screen.getByText('Analyzing your dataset...')).toBeInTheDocument();
  });

  it('shows empty state when no suggestions', () => {
    const SuggestionCards = require('../SuggestionCards').default;
    
    render(
      <SuggestionCards
        suggestions={[]}
        onApply={vi.fn()}
        onFeedback={vi.fn()}
        isLoading={false}
      />
    );

    expect(screen.getByText('No Suggestions Yet')).toBeInTheDocument();
  });
});

describe('ConfidenceIndicator', () => {
  it('displays correct confidence level', () => {
    const ConfidenceIndicator = require('../ConfidenceIndicator').default;
    
    const { rerender } = render(<ConfidenceIndicator confidence={0.9} />);
    expect(screen.getByText('High')).toBeInTheDocument();
    expect(screen.getByText('90%')).toBeInTheDocument();

    rerender(<ConfidenceIndicator confidence={0.5} />);
    expect(screen.getByText('Low')).toBeInTheDocument();
    expect(screen.getByText('50%')).toBeInTheDocument();
  });
});