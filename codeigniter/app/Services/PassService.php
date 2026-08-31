<?php

namespace App\Services;

use Endroid\QrCode\Builder\Builder;
use Mpdf\Mpdf;

final class PassService
{
    public function qrDataUri(string $token): string
    {
        $result = (new Builder(data: $token, size: 280, margin: 12))->build();
        return $result->getDataUri();
    }

    public function pdf(array $registration, string $token): string
    {
        $directory = WRITEPATH . 'passes/';
        if (! is_dir($directory)) mkdir($directory, 0700, true);
        $path = $directory . bin2hex(random_bytes(16)) . '.pdf';
        $qr = $this->qrDataUri($token);
        $html = view('passes/pdf', ['registration'=>$registration,'qr'=>$qr]);
        $pdf = new Mpdf(['tempDir'=>WRITEPATH.'cache']);
        $pdf->WriteHTML($html);
        $pdf->Output($path, 'F');
        return $path;
    }
}