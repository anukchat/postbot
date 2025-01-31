// src/components/Editor/PublishModal.tsx
import React, { useState } from 'react';
import Modal from 'react-modal';
import { useEditorStore } from '../../store/editorStore';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';

const localizer = momentLocalizer(moment);

// Set the app element
Modal.setAppElement('#root'); // or the appropriate element ID for your app

interface PublishModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PublishModal: React.FC<PublishModalProps> = ({ isOpen, onClose }) => {
  const { currentPost, schedulePost } = useEditorStore();
  const [platform, setPlatform] = useState('twitter');
  const [selectedDate, setSelectedDate] = useState(new Date());

  const handleSchedule = () => {
    if (currentPost) {
      schedulePost(currentPost, platform, selectedDate);
    }
    onClose();
  };

  const customStyles = {
    content: {
      top: '50%',
      left: '50%',
      right: 'auto',
      bottom: 'auto',
      marginRight: '-50%',
      transform: 'translate(-50%, -50%)',
      width: '50%',
      padding: '20px',
      borderRadius: '10px',
      backgroundColor: '#fff',
      boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
      zIndex: 1000, // Add higher z-index for content
    },
    overlay: {
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      zIndex: 999, // Add higher z-index for overlay
    },
  };

  return (
    <Modal isOpen={isOpen} onRequestClose={onClose} style={customStyles}>
      <h2>Schedule Post</h2>
      <label>
        Platform:
        <select value={platform} onChange={(e) => setPlatform(e.target.value)}>
          <option value="twitter">Twitter</option>
          <option value="linkedin">LinkedIn</option>
        </select>
      </label>
      <Calendar
        localizer={localizer}
        events={[]}
        startAccessor="start"
        endAccessor="end"
        style={{ height: 500 }}
        onSelectSlot={(slotInfo: { start: React.SetStateAction<Date>; }) => setSelectedDate(slotInfo.start)}
        selectable
      />
      <button onClick={handleSchedule}>Schedule</button>
    </Modal>
  );
};