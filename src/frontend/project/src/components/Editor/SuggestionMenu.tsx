import React, { useEffect, useRef } from 'react';
import { SlashCommand } from '../../types';

interface SuggestionMenuProps {
    commands: SlashCommand[];
    position: { x: number; y: number };
    onSelect: (command: SlashCommand) => void;
    onClose: () => void;
}

export const SuggestionMenu: React.FC<SuggestionMenuProps> = ({
    commands,
    position,
    onSelect,
    onClose,
}) => {
    const menuRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                onClose();
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [onClose]);

    const handleItemClick = (command: SlashCommand) => {
        onSelect(command);
    };

    if (commands.length === 0) {
        return null;
    }

    return (
        <div
            ref={menuRef}
            style={{
                position: 'absolute',
                top: position.y,
                left: position.x,
                zIndex: 100,
                backgroundColor: 'white',
                border: '1px solid #ccc',
                borderRadius: '4px',
                boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
            }}
        >
            {commands.map((command) => (
                <div
                    key={command.id}
                    className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                    onClick={() => handleItemClick(command)}
                >
                    {command.title}
                </div>
            ))}
        </div>
    );
};