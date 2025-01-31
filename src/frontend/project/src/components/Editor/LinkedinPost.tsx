import React, { useCallback, useState, useRef, useEffect } from 'react';
import { useEditorStore } from '../../store/editorStore';
import { EditorStatusBar } from './EditorStatusBar';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';

export const LinkedinPost: React.FC = () => {
    const { currentPost, fetchPosts, updateContent } = useEditorStore();
    const textAreaRef = useRef<HTMLTextAreaElement>(null);
    const [selection, setSelection] = useState({ start: 0, end: 0 });
    const isUpdatingRef = useRef(false);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        fetchPosts({});
    }, [fetchPosts]);

    const handleContentChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const textarea = e.target;
        isUpdatingRef.current = true;
        setSelection({ start: textarea.selectionStart, end: textarea.selectionEnd });
        updateContent(textarea.value);
    }, [updateContent]);

    useEffect(() => {
        if (textAreaRef.current && isUpdatingRef.current) {
            textAreaRef.current.setSelectionRange(selection.start, selection.end);
            textAreaRef.current.focus();
            isUpdatingRef.current = false;
        }
    }, [currentPost?.content, selection]);

    return (
        <div className="flex flex-col h-full" ref={containerRef}>
            <div className="flex-1 relative overflow-auto">
                <PanelGroup direction="horizontal">
                    <Panel defaultSize={50}>
                        <textarea
                            ref={textAreaRef}
                            className="w-full h-full p-4 resize-none focus:outline-none dark:bg-gray-900 dark:text-white"
                            value={currentPost?.linkedin_post || ''}
                            onChange={handleContentChange}
                            onSelect={(e) =>
                                setSelection({
                                    start: e.currentTarget.selectionStart,
                                    end: e.currentTarget.selectionEnd,
                                })
                            }
                            style={{
                                overflowAnchor: 'none',
                                overscrollBehavior: 'none',
                            }}
                            placeholder="What do you want to talk about?"
                        />
                    </Panel>
                    <PanelResizeHandle className="w-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 cursor-col-resize" />
                    <Panel defaultSize={50}>
                        <div className="h-full overflow-auto p-4 max-w-none">
                            <div className="linkedin-post-preview">
                                <p>{currentPost?.linkedin_post}</p>
                            </div>
                        </div>
                    </Panel>
                </PanelGroup>
            </div>
            {currentPost && <EditorStatusBar post={currentPost} />}
        </div>
    );
};
