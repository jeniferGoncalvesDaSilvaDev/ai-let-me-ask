import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [rooms, setRooms] = useState([]);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [newRoomName, setNewRoomName] = useState('');
  const [newRoomDescription, setNewRoomDescription] = useState('');
  const [newQuestion, setNewQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [showCreateRoom, setShowCreateRoom] = useState(false);

  // Fetch rooms on component mount
  useEffect(() => {
    fetchRooms();
  }, []);

  // Fetch questions when room is selected
  useEffect(() => {
    if (selectedRoom) {
      fetchQuestions(selectedRoom.id);
    }
  }, [selectedRoom]);

  const fetchRooms = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/rooms`);
      const data = await response.json();
      setRooms(data);
    } catch (error) {
      console.error('Error fetching rooms:', error);
    }
  };

  const fetchQuestions = async (roomId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/rooms/${roomId}/questions`);
      const data = await response.json();
      setQuestions(data);
    } catch (error) {
      console.error('Error fetching questions:', error);
    }
  };

  const createRoom = async (e) => {
    e.preventDefault();
    if (!newRoomName.trim() || !newRoomDescription.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/rooms`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newRoomName,
          description: newRoomDescription,
        }),
      });

      if (response.ok) {
        setNewRoomName('');
        setNewRoomDescription('');
        setShowCreateRoom(false);
        fetchRooms();
      }
    } catch (error) {
      console.error('Error creating room:', error);
    } finally {
      setLoading(false);
    }
  };

  const createQuestion = async (e) => {
    e.preventDefault();
    if (!newQuestion.trim() || !selectedRoom) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/rooms/${selectedRoom.id}/questions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: newQuestion,
        }),
      });

      if (response.ok) {
        setNewQuestion('');
        fetchQuestions(selectedRoom.id);
        fetchRooms(); // Update question count
      }
    } catch (error) {
      console.error('Error creating question:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAudioUpload = async (e) => {
    const file = e.target.files[0];
    if (!file || !selectedRoom) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('audio', file);

      const response = await fetch(`${API_BASE_URL}/api/rooms/${selectedRoom.id}/audio`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        fetchQuestions(selectedRoom.id);
        fetchRooms(); // Update question count
      }
    } catch (error) {
      console.error('Error uploading audio:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900">
              🚀 NLW Agents API
            </h1>
            <button
              onClick={() => setShowCreateRoom(!showCreateRoom)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Nova Sala
            </button>
          </div>
          <p className="text-gray-600 mt-2">
            Plataforma de perguntas e respostas com IA integrada
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Rooms List */}
          <div className="lg:col-span-1">
            <h2 className="text-xl font-semibold mb-4">Salas</h2>
            
            {/* Create Room Form */}
            {showCreateRoom && (
              <div className="bg-white p-4 rounded-lg shadow-sm border mb-4">
                <form onSubmit={createRoom} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Nome da Sala
                    </label>
                    <input
                      type="text"
                      value={newRoomName}
                      onChange={(e) => setNewRoomName(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Digite o nome da sala"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Descrição
                    </label>
                    <textarea
                      value={newRoomDescription}
                      onChange={(e) => setNewRoomDescription(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Descreva a sala"
                      rows={3}
                      required
                    />
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="submit"
                      disabled={loading}
                      className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
                    >
                      {loading ? 'Criando...' : 'Criar'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowCreateRoom(false)}
                      className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 transition-colors"
                    >
                      Cancelar
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Rooms Grid */}
            <div className="space-y-3">
              {rooms.map((room) => (
                <div
                  key={room.id}
                  onClick={() => setSelectedRoom(room)}
                  className={`p-4 rounded-lg border cursor-pointer transition-all ${
                    selectedRoom?.id === room.id
                      ? 'bg-blue-50 border-blue-200'
                      : 'bg-white border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <h3 className="font-semibold text-gray-900">{room.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{room.description}</p>
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-xs text-gray-500">
                      {room.question_count} pergunta(s)
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(room.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Questions and Chat */}
          <div className="lg:col-span-2">
            {selectedRoom ? (
              <>
                <div className="bg-white rounded-lg shadow-sm border">
                  <div className="p-6 border-b">
                    <h2 className="text-xl font-semibold">{selectedRoom.name}</h2>
                    <p className="text-gray-600 mt-1">{selectedRoom.description}</p>
                  </div>

                  {/* Questions List */}
                  <div className="p-6 max-h-96 overflow-y-auto">
                    {questions.length === 0 ? (
                      <div className="text-center text-gray-500 py-8">
                        Nenhuma pergunta ainda. Faça a primeira pergunta!
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {questions.map((question) => (
                          <div key={question.id} className="space-y-2">
                            {/* Question */}
                            <div className="flex justify-end">
                              <div className="bg-blue-600 text-white p-3 rounded-lg rounded-br-none max-w-md">
                                <p>{question.content}</p>
                                <span className="text-xs text-blue-100 mt-1 block">
                                  {new Date(question.created_at).toLocaleString()}
                                </span>
                              </div>
                            </div>
                            
                            {/* Answer */}
                            {question.answer && (
                              <div className="flex justify-start">
                                <div className="bg-gray-100 text-gray-800 p-3 rounded-lg rounded-bl-none max-w-md">
                                  <p>{question.answer}</p>
                                  <span className="text-xs text-gray-500 mt-1 block">
                                    IA • {new Date(question.created_at).toLocaleString()}
                                  </span>
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Input Area */}
                  <div className="p-6 border-t">
                    <form onSubmit={createQuestion} className="space-y-4">
                      <div className="flex gap-2">
                        <input
                          type="text"
                          value={newQuestion}
                          onChange={(e) => setNewQuestion(e.target.value)}
                          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="Digite sua pergunta..."
                          required
                        />
                        <button
                          type="submit"
                          disabled={loading}
                          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                        >
                          {loading ? '...' : 'Enviar'}
                        </button>
                      </div>
                    </form>

                    {/* Audio Upload */}
                    <div className="mt-4 pt-4 border-t">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Ou envie um áudio:
                      </label>
                      <input
                        type="file"
                        accept=".webm,.wav,.mp3"
                        onChange={handleAudioUpload}
                        className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                      />
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
                <div className="text-gray-500">
                  <h3 className="text-lg font-semibold mb-2">
                    Selecione uma sala para começar
                  </h3>
                  <p>Escolha uma sala existente ou crie uma nova para fazer perguntas</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;