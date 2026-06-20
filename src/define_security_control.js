import React, { useState } from 'react';
import "./define_security_control.css";
import { eel } from './App';

function DefineSecurityControl({ refreshControls }) {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [operatorName, setOperator] = useState('');

    const handleSave = async (event) => {
        event.preventDefault();
        eel.insert_security_control(title, description, operatorName)((response) => {
            console.log('Response from Python:', response);
            refreshControls(); // Call refreshControls to update the list
        });
    };

    return (
        <div className="definition-security-control">
            <form onSubmit={handleSave}>
                <label className="form-label">
                    Title
                    <input type="text" placeholder="Enter title" className="input-field" value={title} onChange={e => setTitle(e.target.value)} />
                </label>
                <label className="form-label">
                    Description
                    <textarea placeholder="Enter description" className="textarea-field" value={description} onChange={e => setDescription(e.target.value)}></textarea>
                </label>
                <label className="form-label">
                    Operator
                    <input type="text" placeholder="Enter assigned operator" className="input-field" value={operatorName} onChange={e => setOperator(e.target.value)} />
                </label>
                
                <button type="submit" className="save-button">Save</button>
            </form>
        </div>
    );
}

export default DefineSecurityControl;
