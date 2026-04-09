import React, { useEffect, useRef } from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription,
  DialogFooter
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Printer, Download, X } from 'lucide-react';
// @ts-ignore
import QRCode from 'qrcode';

interface QRCodeDialogProps {
  isOpen: boolean;
  onClose: () => void;
  data: string;
  label: string;
}

const QRCodeDialog: React.FC<QRCodeDialogProps> = ({ isOpen, onClose, data, label }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (isOpen && canvasRef.current && data) {
      // Optimization: Compress/Scale QR on client canvas
      QRCode.toCanvas(canvasRef.current, data, {
        width: 200,
        margin: 2,
        color: {
          dark: '#000000',
          light: '#ffffff',
        },
      }, (error: any) => {
        if (error) console.error('QR Alpha Generation Error:', error);
      });
    }
  }, [isOpen, data]);

  const handlePrint = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const dataUrl = canvas.toDataURL();
    const windowContent = `<!DOCTYPE html><html><head><title>Print Label</title></head><body><div style="text-align:center;"><img src="${dataUrl}" /><p style="font-family:sans-serif;font-weight:bold;">${label}</p></div><script>window.onload = function() { window.print(); window.close(); }</script></body></html>`;
    const printWin = window.open('', '', 'width=400,height=400');
    printWin?.document.open();
    printWin?.document.write(windowContent);
    printWin?.document.close();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md bg-card border-primary/20">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold tracking-tight">Generate Asset Label</DialogTitle>
          <DialogDescription>
            High-resolution compressed QR code for physical tagging.
          </DialogDescription>
        </DialogHeader>
        <div className="flex flex-col items-center justify-center p-6 bg-white rounded-xl shadow-inner border">
          <canvas ref={canvasRef} className="max-w-full h-auto drop-shadow-md" />
          <p className="mt-4 font-mono text-sm font-bold text-slate-800 uppercase tracking-widest">{label}</p>
        </div>
        <DialogFooter className="flex sm:justify-between gap-2">
          <Button variant="outline" onClick={onClose}>
            <X className="h-4 w-4 mr-2" /> Cancel
          </Button>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => {
              const link = document.createElement('a');
              link.download = `QR_${label}.png`;
              link.href = canvasRef.current?.toDataURL() || '';
              link.click();
            }}>
              <Download className="h-4 w-4 mr-2" /> Download
            </Button>
            <Button onClick={handlePrint} className="bg-primary hover:bg-primary/90">
              <Printer className="h-4 w-4 mr-2" /> Print Label
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default QRCodeDialog;
