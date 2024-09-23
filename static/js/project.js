// LINE UPDATE
function updateLineNumbers() {
    const textarea = document.querySelector(".editor-content");
    const lineNumbers = document.getElementById("lineNumbers");
    
    const lines = textarea.value.split("\n").length;
    lineNumbers.innerHTML = "";

    for (let i = 1; i <= lines; i++) {
        lineNumbers.innerHTML += i + "<br>";
    }

    // Perbarui tinggi textarea dan line numbers agar sesuai dengan konten
    textarea.style.height = 'auto';  // Set auto height to reset
    textarea.style.height = textarea.scrollHeight + 'px';  // Set height based on scrollHeight
    lineNumbers.style.height = textarea.scrollHeight + 'px';  // Sync height with content
}

// Panggil fungsi saat halaman dimuat untuk inisialisasi
updateLineNumbers();

    // Sinkronkan scroll antara line-numbers dan editor-content
    const editorContent = document.querySelector('.editor-content');
    const lineNumbers = document.querySelector('.lineNumbers');

    editorContent.addEventListener('scroll', function() {
        lineNumbers.scrollTop = editorContent.scrollTop;
    });


 // Update line numbers setiap kali pengguna mengetik di textarea
 editorContent.addEventListener('input', updateLineNumbers);


// Fungsi untuk menampilkan LaTeX di dalam halaman
            document.getElementById("previewLatex").onclick = function() {
            // Ambil konten LaTeX dari textarea
            let latexCode = document.querySelector(".editor-content").value;
            
            // Masukkan konten LaTeX ke dalam elemen HTML untuk preview
            document.getElementById("latexPreview").innerHTML = "$$" + latexCode + "$$";
            
            // Render ulang LaTeX menggunakan MathJax
            MathJax.typeset();
            
        };

        // Fungsi untuk mengirim LaTeX ke Overleaf saat tombol "Edit with LaTeX" diklik
        document.getElementById("overleafForm").onsubmit = function() {
            // Ambil konten LaTeX dari textarea
            let latexCode = document.querySelector(".editor-content").value;

            // Konversi konten LaTeX ke Base64
            let base64Latex = btoa(latexCode);

            // Masukkan hasil Base64 ke dalam input form hidden untuk dikirim ke Overleaf
            document.getElementById("snip_uri").value = "data:application/x-tex;base64," + base64Latex;
        };


