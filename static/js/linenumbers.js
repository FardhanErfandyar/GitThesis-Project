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



