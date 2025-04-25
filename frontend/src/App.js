import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Slider,
  TextField,
  Typography,
  Paper,
  Grid,
  Button
} from '@mui/material';
import axios from 'axios';

function App() {
  const [cameraControls, setCameraControls] = useState({
    phi: 75,
    theta: 30,
    zoom: 0.7
  });
  
  const [function_str, setFunctionStr] = useState('0.5 * np.sin(2 * np.pi * t)');
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  const generatePreview = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/generate_preview', {
        function: function_str,
        camera_phi: cameraControls.phi,
        camera_theta: cameraControls.theta,
        zoom_level: cameraControls.zoom
      }, {
        responseType: 'blob'
      });
      
      const url = URL.createObjectURL(response.data);
      setPreviewUrl(url);
    } catch (error) {
      console.error('Error generating preview:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    generatePreview();
  }, []);

  const handleControlChange = (control) => (event, value) => {
    setCameraControls(prev => ({
      ...prev,
      [control]: value
    }));
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        交互式Manim动画生成器
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: '500px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            {loading ? (
              <Typography>生成预览中...</Typography>
            ) : (
              previewUrl && <img src={previewUrl} alt="Preview" style={{ maxWidth: '100%', maxHeight: '100%' }} />
            )}
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              控制面板
            </Typography>
            
            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>函数表达式</Typography>
              <TextField
                fullWidth
                value={function_str}
                onChange={(e) => setFunctionStr(e.target.value)}
                helperText="使用 np.sin, np.cos, np.pi 等numpy函数"
              />
            </Box>
            
            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>相机角度 φ (Phi)</Typography>
              <Slider
                value={cameraControls.phi}
                onChange={handleControlChange('phi')}
                min={0}
                max={360}
                valueLabelDisplay="auto"
              />
            </Box>
            
            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>相机角度 θ (Theta)</Typography>
              <Slider
                value={cameraControls.theta}
                onChange={handleControlChange('theta')}
                min={-180}
                max={180}
                valueLabelDisplay="auto"
              />
            </Box>
            
            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>缩放级别</Typography>
              <Slider
                value={cameraControls.zoom}
                onChange={handleControlChange('zoom')}
                min={0.1}
                max={2}
                step={0.1}
                valueLabelDisplay="auto"
              />
            </Box>
            
            <Button
              variant="contained"
              fullWidth
              onClick={generatePreview}
              disabled={loading}
            >
              生成预览
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default App; 